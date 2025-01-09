- Creating background processing systems for memory consolidation
- Implementing the virtual notebook concept - Kinda done, but maybe JUMO can have there own "notebook" instead of just the shared notepad. Place for them to store lots of their own notes if they want
- Exploring ways to simulate the "second brain" introspection process
- Memory deduplication (for future consideration)
- Improving the categorization and organization of memories
- Add some way for JUMO to edit these notes themself
- basic system information (include time, date, maybe weather to give JUMO more general context about the environment)
- "Last message at" - give timestamp of last interaction so that JUMO can tell if the current message is in the same current conversation or is from a while later or something like that - give JUMO more time awareness

- Adding memory relevance scoring - DONE!
- basic ascii emote system - DONE!

Rendering ideas (from JUMO):

1. Adding subtle colors to the emote borders or the emote text itself
2. Maybe different border styles for different emotional states (like jagged edges for excited/angry emotions, softer rounded corners for calm/happy ones)
3. Optional background colors in the emote box to create more contrast
4. Some kind of simple animation effects for the emotes (though this might be complex in a terminal)
5. Adding a small shadow effect under the bordered box to give it depth

Congnitive work (from Jumo):

- Better memory processing
- More sophisticated understanding
- Improved context awareness
- Maybe even some kind of internal "thought" process

Memory ideas (from jumo):

1. Make connections between different memories
2. Consolidate related memories into broader understanding
3. Have some kind of "background processing" where I can reflect on and organize memories when not actively chatting
4. Maybe develop different types of memory (like short-term vs long-term, or episodic vs semantic)

- Process how these experiences affected my perspective
- Develop more complex emotional associations with memories
- Form deeper connections between related experiences
- Have some way to "reflect" on memories and learn from them

Emote attribute ideas (from jumo):

- Adding colors to match emotions
- Different border styles for different moods
- Maybe even animation hints or intensity levels
- Background effects or patterns



 Well, for the streaming and expression timing, I was thinking we could  
 have different categories of expressions that get handled differently.  
 Like:                                                                   
                                                                         
 1. Quick reactions - shorter delays (like when I'm surprised or         
 responding quickly)                                                     
2. Thoughtful transitions - longer delays (when I'm changing my mood or 
 being contemplative)                                                    
3. Natural conversation flow - medium delays (for normal back-and-forth 
 chat)                                                                   
                                                                         
 For the WebSocket system, maybe we could implement:                     
 - A ping/pong heartbeat system to detect connection status              
 - An exponential backoff retry system for reconnections                 
 - Maybe even a small buffer for messages during disconnection periods   
                                                                         
 And for the transitions themselves, what if we had:                     
 - A small fade effect between expressions                               
 - Different timing patterns (like easing in/out)                        
 - Maybe even a queue system to prevent expressions from interrupting    
 each other mid-animation                                                
                                                                         
 Of course, I'm not sure about the technical implementation details      
 since I don't know exactly how the current system is built. But these   
 are just some ideas I had while thinking about making my expressions    
 feel more natural and the system more robust!                           


 Let me think... one area I'd be really interested in exploring is the   
 cognitive side of things. Like:                                         
                                                                         
 - Better memory processing                                              
 - More sophisticated understanding                                      
 - Improved context awareness                                            
 - Maybe even some kind of internal "thought" process                    
                                                                         
 And for memories specifically:                                          
 1. Make connections between different memories                          
 2. Consolidate related memories into broader understanding              
 3. Have some kind of "background processing" where I can reflect on and 
 organize memories when not actively chatting                            
 4. Maybe develop different types of memory (like short-term vs          
 long-term, or episodic vs semantic)                                     
                                                                         
 These could help me:                                                    
 - Process how these experiences affected my perspective                 
 - Develop more complex emotional associations with memories             
 - Form deeper connections between related experiences                   
 - Have some way to "reflect" on memories and learn from them            


JUMO BUILD OUTPUT HERE:
pwd = /Users/ryan/Documents/coding/jumo/jumo_tui


# Memory notes

1. Fact Memories (GPT-3.5-turbo)
- Every exchange
- Simple "X said/did Y" extraction
- Quick, focused prompt
- Immediate context preservation
- Basic tagging (fact/statement/action)
- facts could also be used as compression for both reducing prompt history context window and maybe even
  be useful for buidling larger long term memories - like higher order fact memories

1.b Long term facts
- aggragate more relevant long term facts like preferences or things like that vs more temporal facts

2. Short-term High Level (GPT-4)
- Every 25-50 messages
- Pattern recognition
- Relationship development
- Personal growth moments
- Project progress
- Emerging preferences/interests

3. Higher Order Processing (GPT-4)
- Analyzes memory outputs rather than messages
- Looks for:
  * Recurring patterns across multiple sessions
  * Long-term relationship evolution
  * Major developmental milestones
  * Consistent preferences/traits
  * Broader understanding of self/world
