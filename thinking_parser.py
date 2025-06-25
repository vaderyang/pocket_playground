import re
import chainlit as cl

class StreamingThinkingParser:
    def __init__(self):
        self.buffer = ""
        self.in_thinking = False
        self.thinking_content = ""
        self.regular_content = ""
        self.thinking_step = None
        self.message = None
    
    async def process_chunk(self, chunk_content):
        """Process streaming chunk and handle thinking tags"""
        self.buffer += chunk_content
        
        # Check for opening thinking tag
        if '<think>' in self.buffer and not self.in_thinking:
            # Extract content before <think>
            parts = self.buffer.split('<think>', 1)
            if parts[0]:
                self.regular_content += parts[0]
                await self._update_message()
            
            # Start thinking mode
            self.in_thinking = True
            self.buffer = parts[1] if len(parts) > 1 else ""
            await self._start_thinking_step()
        
        # Check for closing thinking tag
        elif '</think>' in self.buffer and self.in_thinking:
            # Extract thinking content
            parts = self.buffer.split('</think>', 1)
            self.thinking_content += parts[0]
            await self._update_thinking_step()
            
            # End thinking mode
            self.in_thinking = False
            self.buffer = parts[1] if len(parts) > 1 else ""
            await self._end_thinking_step()
        
        # Regular content processing
        elif not self.in_thinking:
            self.regular_content += self.buffer
            self.buffer = ""
            await self._update_message()
        
        # Thinking content processing
        else:
            self.thinking_content += self.buffer
            self.buffer = ""
            await self._update_thinking_step()
    
    async def _start_thinking_step(self):
        """Start a new thinking step"""
        self.thinking_step = cl.Step(name="🤔 Thinking Process", type="run")
        await self.thinking_step.__aenter__()
    
    async def _update_thinking_step(self):
        """Update thinking step content"""
        if self.thinking_step:
            self.thinking_step.output = self.thinking_content
            await self.thinking_step.update()
    
    async def _end_thinking_step(self):
        """End the thinking step"""
        if self.thinking_step:
            self.thinking_step.output = self.thinking_content
            await self.thinking_step.__aexit__(None, None, None)
            self.thinking_step = None
            self.thinking_content = ""
    
    async def _update_message(self):
        """Update the main message"""
        if not self.message:
            self.message = cl.Message(content=self.regular_content)
            await self.message.send()
        else:
            self.message.content = self.regular_content
            await self.message.update()
    
    async def finalize(self):
        """Finalize any remaining content"""
        if self.buffer:
            if self.in_thinking:
                self.thinking_content += self.buffer
                await self._update_thinking_step()
                await self._end_thinking_step()
            else:
                self.regular_content += self.buffer
                await self._update_message()
        # Ensure any open thinking step is completed
        elif self.thinking_step:
            await self._end_thinking_step()

def parse_thinking_tags(response_text):
    """Parse <think>...</think> tags from response"""
    thinking_pattern = r'<think>(.*?)</think>'
    thinking_matches = re.findall(thinking_pattern, response_text, re.DOTALL)
    
    # Remove thinking tags from main response
    clean_response = re.sub(thinking_pattern, '', response_text, flags=re.DOTALL).strip()
    
    return thinking_matches, clean_response

async def display_thinking_and_response(response_text):
    """Display thinking process and final response separately"""
    thinking_parts, clean_response = parse_thinking_tags(response_text)
    
    # Display thinking process if present
    if thinking_parts:
        thinking_content = ""
        for i, thinking in enumerate(thinking_parts, 1):
            thinking_content += f"**Step {i}:**\n{thinking.strip()}\n\n"
        
        async with cl.Step(name="🤔 Thinking Process", type="run") as step:
            step.output = thinking_content.strip()
    
    # Display final response
    await cl.Message(content=clean_response).send()