import os
import asyncio
import logging
import random
import hashlib
from typing import Optional
from openai import AsyncOpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

class PoemService:
    """Service for generating poems using OpenAI or fallback mock AI"""
    
    def __init__(self):
        """Initialize the poem service with enhanced error handling"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self._api_key_valid = False
        
        if self.openai_api_key and self.openai_api_key.strip():
            # Validate API key format
            if self._validate_api_key_format(self.openai_api_key):
                try:
                    self.client = AsyncOpenAI(
                        api_key=self.openai_api_key,
                        timeout=30.0  # 30 second timeout
                    )
                    self._api_key_valid = True
                    logger.info("OpenAI client initialized successfully with valid API key")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                    logger.warning("Using mock AI fallback due to client initialization error")
            else:
                logger.warning("Invalid OpenAI API key format. Using mock AI fallback.")
        else:
            logger.warning("No OpenAI API key found. Using mock AI fallback.")
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate OpenAI API key format"""
        if not api_key:
            return False
        
        # OpenAI API keys typically start with 'sk-' and have specific length
        if api_key.startswith('sk-') and len(api_key) > 20:
            return True
        
        logger.warning("API key does not match expected OpenAI format")
        return False
    
    async def generate_poem(self, theme: str, style: str = "creative", length: str = "medium") -> str:
        """
        Generate a poem using OpenAI or fallback to mock AI
        
        Args:
            theme: The theme or topic for the poem
            style: The style of poem (creative, haiku, sonnet, free_verse, rhyming)
            length: The length of poem (short, medium, long)
            
        Returns:
            str: The generated poem text
        """
        # Input validation
        if not theme or not theme.strip():
            raise ValueError("Theme cannot be empty")
        
        theme = theme.strip()
        logger.info(f"Generating poem for theme: '{theme}', style: '{style}', length: '{length}'")
        
        # Try OpenAI first if available
        if self.client and self.openai_api_key:
            try:
                logger.info("Attempting OpenAI poem generation")
                result = await self._generate_with_openai(theme, style, length)
                logger.info("Successfully generated poem using OpenAI")
                return result
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {str(e)}")
                logger.info("Falling back to mock poem generation")
                
        # Fallback to mock poems
        logger.info("Using mock poem generation")
        return await self._generate_mock_poem(theme, style, length)
    
    async def _generate_with_openai(self, theme: str, style: str, length: str) -> str:
        """Generate poem using OpenAI API with robust error handling"""
        
        # Validate inputs
        if not self.client:
            raise ValueError("OpenAI client not initialized")
            
        # Define length instructions with token considerations
        length_instructions = {
            "short": "Write a concise poem (4-6 lines) that captures the essence beautifully",
            "medium": "Write a well-structured poem (8-12 lines) with rich imagery",  
            "long": "Write an expansive poem (16-20 lines) with deep emotional resonance"
        }
        
        # Enhanced style instructions
        style_instructions = {
            "haiku": "Write a traditional haiku following the 5-7-5 syllable pattern exactly. Focus on nature imagery and a moment in time",
            "sonnet": "Write a Shakespearean sonnet with exactly 14 lines following ABAB CDCD EFEF GG rhyme scheme",
            "free_verse": "Write a free verse poem with natural speech rhythms, no forced rhymes, focusing on imagery and emotion",
            "rhyming": "Write a poem with a consistent, pleasing rhyme scheme (AABB or ABAB). Make rhymes feel natural, not forced",
            "creative": "Write an innovative poem using creative techniques: metaphors, symbolism, unique perspectives, and emotional depth"
        }
        
        # Add variation to prevent repetitive responses
        variation_phrases = [
            "Create a unique and original",
            "Compose a fresh and inspiring", 
            "Write a distinctive and creative",
            "Craft a beautiful and meaningful",
            "Generate an expressive and heartfelt"
        ]
        
        approach_styles = [
            "Focus on creating vivid imagery and emotional depth",
            "Emphasize metaphorical language and lyrical beauty", 
            "Use rich sensory details and evocative language",
            "Incorporate symbolism and deeper meaning",
            "Blend rhythm, imagery, and emotional resonance"
        ]
        
        # Add randomization to make each request unique
        seed = hash(f"{theme}-{style}-{length}-{datetime.now().microsecond}") % len(variation_phrases)
        variation = variation_phrases[seed % len(variation_phrases)]
        approach = approach_styles[seed % len(approach_styles)]
        
        # Build the prompt with variation and make the theme requirement explicit
        prompt = f"""
{variation} {length_instructions.get(length, length_instructions['medium'])} about "{theme}".

IMPORTANT: The poem must clearly reference and be grounded in the provided theme: "{theme}". Use the theme as the central focus throughout. If the theme contains multiple words, use them naturally in the poem (do not invent an unrelated topic).

{style_instructions.get(style, style_instructions['creative'])}

{approach}. The poem should be:
- Directly connected to the given theme and include related wording or imagery
- Emotionally engaging and thoughtful
- Rich in vivid imagery and metaphors
- Well-structured with good rhythm and flow
- Original and creative
- Beautifully written with literary merit

Please return only the poem text without any additional commentary, explanations, or quotation marks.
        """.strip()
        
        # Retry logic for API calls
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Enhanced system prompts for variety
                system_prompts = [
                    "You are a world-renowned poet with exceptional talent for creating beautiful, meaningful poetry. Your poems touch hearts and inspire souls with original, emotionally resonant verses.",
                    "You are an acclaimed poet known for crafting verses that capture the essence of human experience. Each poem is unique, filled with imagery that speaks to the soul.",
                    "You are a master of poetic expression, weaving words into tapestries of emotion and meaning. You create original verses that illuminate life's beauty through metaphor.",
                    "You are a visionary poet whose words paint vivid pictures. You excel at creating fresh, original poetry that combines emotional depth with artistic beauty."
                ]
                
                # Dynamic system prompt selection
                system_prompt = system_prompts[hash(f"{theme}-{style}-{attempt}-{datetime.now().microsecond}") % len(system_prompts)]
                
                # Optimized parameters for better poem generation
                # Lower temperature slightly to improve relevance to theme while keeping some creativity
                temperature = random.uniform(0.55, 0.8)
                presence_penalty = random.uniform(0.0, 0.3)  # Encourage new topics lightly
                frequency_penalty = random.uniform(0.0, 0.3)  # Reduce repetition lightly
                
                # Determine max tokens based on length
                max_tokens_map = {"short": 200, "medium": 350, "long": 500}
                max_tokens = max_tokens_map.get(length, 350)
                
                logger.info(f"OpenAI API call attempt {attempt + 1}/{max_retries}")
                
                response = await self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                    timeout=30.0  # 30 second timeout
                )
                
                # Extract and validate poem
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("Empty response from OpenAI API")
                    
                poem_text = response.choices[0].message.content.strip()

                # Post-generation sanity check: ensure poem references the theme (or at least a stem of it)
                theme_tokens = [t.lower() for t in theme.split() if len(t) > 2]
                poem_lower = poem_text.lower()
                if theme_tokens:
                    found = any(token in poem_lower for token in theme_tokens)
                else:
                    found = theme.lower() in poem_lower

                if not found:
                    # If theme not referenced, consider this attempt a miss and retry (up to retries)
                    logger.warning("Generated poem does not reference the theme; retrying to improve relevance")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5 + random.random())
                        continue
                    else:
                        # Fall back to returning poem even if not matched after retries
                        logger.warning("Final attempt did not include theme; will perform a focused retry forcing the theme phrase")
                        # Perform a focused follow-up attempt that *must* include the exact theme phrase
                        try:
                            focused_prompt = prompt + f"\n\nIMPORTANT: The poem MUST include the exact phrase \"{theme}\" at least once. Do not omit or change this phrase. Return only the poem text."
                            logger.info("Performing focused OpenAI call to enforce theme inclusion")
                            focused_response = await self.client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": focused_prompt}
                                ],
                                max_tokens=max_tokens,
                                temperature=0.3,
                                presence_penalty=0.0,
                                frequency_penalty=0.0,
                                timeout=30.0
                            )
                            if focused_response.choices and focused_response.choices[0].message.content:
                                poem_text = focused_response.choices[0].message.content.strip()
                                poem_text = self._clean_poem_text(poem_text)
                                # Final check
                                if theme.lower() in poem_text.lower():
                                    logger.info("Focused retry succeeded and included the theme phrase")
                                    return poem_text
                                else:
                                    logger.warning("Focused retry did not include theme despite instruction; returning it anyway")
                                    return poem_text
                        except Exception as fe:
                            logger.error(f"Focused retry failed: {fe}")
                            # Fall through to return the last poem_text
                
                # Basic validation
                if len(poem_text) < 10:
                    raise ValueError("Generated poem is too short")
                    
                # Remove any unwanted prefixes/suffixes
                poem_text = self._clean_poem_text(poem_text)
                
                logger.info(f"Successfully generated {len(poem_text)} character poem using OpenAI")
                return poem_text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle specific OpenAI errors
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Rate limit hit, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error("Rate limit exceeded, all retries exhausted")
                        raise Exception("OpenAI rate limit exceeded")
                        
                elif "quota" in error_msg or "insufficient_quota" in error_msg:
                    logger.error("OpenAI quota exceeded")
                    raise Exception("OpenAI quota exceeded - please check billing")
                    
                elif "timeout" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * (attempt + 1)
                        logger.warning(f"Timeout error, retrying in {delay}s")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception("OpenAI API timeout")
                        
                else:
                    logger.error(f"OpenAI API error on attempt {attempt + 1}: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay)
                        continue
                    else:
                        raise Exception(f"OpenAI API failed after {max_retries} attempts: {str(e)}")
        
        raise Exception("All OpenAI API attempts failed")
    
    def _clean_poem_text(self, poem_text: str) -> str:
        """Clean and format the poem text"""
        # Remove common unwanted prefixes
        prefixes_to_remove = [
            "Here's a poem", "Here is a poem", "Here's your poem", 
            "I'll write", "Let me write", "A poem about",
            "Title:", "Poem:", "Verse:"
        ]
        
        lines = poem_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
                
            # Check if line starts with unwanted prefix
            should_skip = False
            for prefix in prefixes_to_remove:
                if line.lower().startswith(prefix.lower()):
                    should_skip = True
                    break
                    
            if not should_skip:
                # Remove quotes if the entire line is quoted
                if (line.startswith('"') and line.endswith('"')) or (line.startswith("'") and line.endswith("'")):
                    line = line[1:-1]
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    async def _generate_mock_poem(self, theme: str, style: str, length: str) -> str:
        """Generate poem using mock AI (fallback) with variety and randomization"""
        import random
        import hashlib
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.8, 1.5))
        
        # Create a unique seed based on theme, style, length, and current time
        seed_string = f"{theme.lower()}-{style}-{length}-{datetime.now().microsecond}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Enhanced poem templates with multiple variations
        poem_templates = {
            "love": {
                "short": [
                    "Love blooms like {flower} in {season},\nTwo souls united beyond all reason.\nIn {adjective} moments we find our way,\nLove's gentle {noun} brightens each day.",
                    "Your {body_part} speaks what words cannot say,\nIn love's embrace we'll always stay.\nThrough {weather} storms and sunny skies,\nOur love's the {noun} that never dies.",
                    "Like {celestial} dancing in the night,\nOur hearts burn with {adjective} light.\nIn {location} or {location} we roam,\nYour love will always be my home."
                ],
                "medium": [
                    "In gardens where the {flower}s grow,\nLove's {adjective} secrets gently flow.\nWith {adjective} words and tender care,\nWe find our {noun} everywhere.\n\nThrough seasons of both joy and {noun},\nOur hearts dance in love's sweet refrain.\nLike {celestial} that shine above,\nWe're bound together by true love.",
                    "Beneath the {adjective} {weather} sky,\nWhere {adjective} dreams learn how to fly,\nLove finds its way through {noun} and space,\nA gentle touch, a warm embrace.\n\nThrough {weather} storms and {adjective} days,\nLove guides us through life's winding maze.\nWith every breath and beating heart,\nWe know we'll never drift apart."
                ],
                "long": [
                    "When {celestial} paint the evening sky,\nAnd gentle {weather} whispers by,\nLove blooms like {flower}s in the spring,\nA {adjective} and precious thing.\n\nIn {location} where the {flower}s grow,\nAnd crystal {noun}s gently flow,\nTwo hearts discover what is true,\nA love that's {adjective} through and through.\n\nThrough {weather} storms and sunny days,\nLove lights our path in countless ways.\nWith {adjective} touch and whispered word,\nOur hearts fly free like soaring bird.\n\nSo let us dance in love's sweet light,\nAnd hold each other through the night.\nFor in this love we've come to know,\nOur souls have found their place to grow."
                ]
            },
            "nature": {
                "short": [
                    "In {location} where {animal}s play,\nNature paints a new display.\nThe {weather} {noun} and {adjective} trees,\nDance together in the breeze.",
                    "Beneath the {adjective} {celestial} above,\nNature shows us how to love.\n{Animal}s sing their {adjective} song,\nWhere wild {flower}s have grown strong.",
                    "{Weather} whispers through the {noun},\nWhere ancient {tree}s have always been.\nIn every leaf and {flower} bright,\nNature fills the world with light."
                ],
                "medium": [
                    "In {location} where {animal}s roam free,\nBeneath the shade of {adjective} tree,\nNature weaves her {adjective} spell,\nStories that the {weather} tell.\n\nThe {noun} flows with {adjective} grace,\nReflecting {celestial}'s gentle face.\nWhile {animal}s dance in morning dew,\nNature's magic shines right through.",
                    "Deep in {location} shadows play,\nWhere {adjective} {tree}s hold sway.\n{Celestial} filters through the leaves,\nAs nature's {noun} softly weaves.\n\nThe {weather} {noun} tells stories old,\nOf seasons past and legends told.\nWhile {animal}s dance through morning mist,\nBy nature's {adjective} hand are kissed."
                ],
                "long": [
                    "In {location} vast and wild and free,\nWhere {animal}s roam beside the sea,\nNature paints with {adjective} hand,\nAcross this {adjective} wonderland.\n\nThe {weather} sings through {tree} tall,\nWhile {flower}s bloom for one and all.\n{Animal}s call from {noun} deep,\nWhere ancient secrets nature keeps.\n\n{Celestial} dance across the sky,\nAs gentle {weather} breezes sigh.\nIn every stone and grain of sand,\nWe see the work of nature's hand.\n\nFrom {location} high to valleys low,\nNature's {adjective} wonders grow.\nA world of beauty, wild and free,\nNature's perfect symphony."
                ]
            },
            "dreams": {
                "short": [
                    "In dreams where {adjective} {animal}s fly,\nBeneath the {weather} {celestial} sky.\nHope and wonder intertwine,\nIn realms both {adjective} and divine.",
                    "When {noun} falls and day is done,\nAnd dreams begin their {adjective} run,\nWe journey to a world unknown,\nWhere {adjective} seeds are freely sown.",
                    "Close your {body_part} and drift away,\nTo where dreams hold {adjective} sway.\nBeyond the boundaries of {noun},\nWhere {adjective} meets the sublime."
                ],
                "medium": [
                    "In castles built of {adjective} light,\nWe wander through the {weather} night.\nWhere {animal}s speak and {flower}s sing,\nAnd {noun} can do most anything.\n\nThrough gardens of the sleeping mind,\nWe leave our {adjective} cares behind.\nAnd in this realm of pure delight,\nOur spirits soar throughout the night.",
                    "When {celestial} begin to fade,\nAnd dreamy {noun}s are softly made,\nWe sail on {weather} winds so high,\nAcross the {adjective} dream-filled sky.\n\nIn lands where {adjective} {animal}s play,\nAnd {flower}s bloom in strange array,\nOur dreams unfold like {noun} bright,\nGuiding us through the night."
                ],
                "long": [
                    "In realm where {adjective} dreams take flight,\nBeyond the veil of day and night,\nWhere {animal}s dance on {weather} air,\nAnd {flower}s bloom beyond compare.\n\nThrough {location} of the sleeping mind,\nWhere {adjective} treasures we can find,\n{Celestial} guide our spirits free,\nTo lands of {noun} and mystery.\n\nIn dreams we ride on {weather} wings,\nWhere every {noun} softly sings,\nAnd {adjective} castles touch the sky,\nWhere hopes and wishes never die.\n\nSo dream, dear soul, and do not fear,\nFor in your dreams, all truth is clear.\nA world where {noun} and joy run free,\nAnd you can be all you can be."
                ]
            }
        }
        
        # Word banks for template filling
        word_banks = {
            "flower": ["roses", "lilies", "daisies", "tulips", "orchids", "sunflowers", "peonies", "violets"],
            "season": ["spring", "summer", "autumn", "winter", "dawn", "twilight"],
            "adjective": ["gentle", "radiant", "peaceful", "vibrant", "serene", "luminous", "graceful", "tender", "mystical", "enchanting"],
            "noun": ["whisper", "melody", "harmony", "symphony", "journey", "treasure", "wonder", "miracle", "magic", "beauty"],
            "body_part": ["eyes", "smile", "heart", "soul", "voice", "touch"],
            "weather": ["misty", "golden", "silver", "crystal", "starlit", "moonlit"],
            "celestial": ["stars", "moon", "sun", "comets", "galaxies", "constellations"],
            "location": ["meadows", "mountains", "forests", "gardens", "valleys", "riversides", "hillsides"],
            "animal": ["birds", "deer", "butterflies", "foxes", "rabbits", "eagles", "dolphins"],
            "tree": ["oaks", "willows", "pines", "maples", "birches", "cedars"]
        }
        
        # Determine theme category or create custom
        theme_lower = theme.lower()
        selected_templates = None
        
        # Match theme to template category
        if any(word in theme_lower for word in ["love", "heart", "romance", "valentine", "relationship"]):
            selected_templates = poem_templates["love"]
        elif any(word in theme_lower for word in ["nature", "forest", "tree", "flower", "mountain", "ocean", "river", "bird", "animal"]):
            selected_templates = poem_templates["nature"]  
        elif any(word in theme_lower for word in ["dream", "sleep", "night", "fantasy", "imagination", "wish"]):
            selected_templates = poem_templates["dreams"]
        
        # Generate poem
        if selected_templates and length in selected_templates:
            template = random.choice(selected_templates[length])
            # Fill template with random words (handle several placeholder case variants)
            for category, words in word_banks.items():
                choices = [random.choice(words) for _ in range(3)]
                replacement = random.choice(choices)
                # Replace common case variants: {category}, {Category}, {CATEGORY}, {CategoryTitle}
                template = template.replace('{' + category + '}', replacement)
                template = template.replace('{' + category.capitalize() + '}', replacement)
                template = template.replace('{' + category.upper() + '}', replacement)
                template = template.replace('{' + category.title() + '}', replacement)

            # Ensure the generated poem references the theme; if not, append a short thematic line
            poem_lower = template.lower()
            theme_tokens = [t.lower() for t in theme.split() if len(t) > 2]
            if theme_tokens and not any(tok in poem_lower for tok in theme_tokens):
                # Append a short concluding line that mentions the theme explicitly
                template = template.rstrip() + f"\n\n(about {theme})"

            return template
        else:
            # Generate custom poem for unique themes
            return await self._generate_custom_theme_poem(theme, style, length, word_banks, random)
    
    async def _generate_custom_theme_poem(self, theme: str, style: str, length: str, word_banks: dict, random_gen) -> str:
        """Generate custom poems for unique themes"""
        
        # Custom templates for any theme
        custom_templates = {
            "short": [
                "Upon the theme of \"{theme}\" I write,\nWith words that dance in {adjective} light.\nInspiration flows like morning dew,\nCreating verses fresh and new.",
                "In contemplation of \"{theme}\" so bright,\nI weave these words with pure delight.\nLet {noun} take its winding course,\nAnd poetry flow from creative source.",
                "The beauty of \"{theme}\" unfolds,\nIn {adjective} stories that poet tells.\nWith {noun} and rhythm combined,\nI craft these verses for heart and mind."
            ],
            "medium": [
                "Upon the canvas of \"{theme}\",\nI paint with words a {adjective} dream.\nWhere thoughts and feelings intertwine,\nAnd create something quite divine.\n\nLet metaphors dance through each line,\nAs imagery and rhythm combine.\nTo bring your vision into view,\nA poem crafted just for you.",
                "In realm of \"{theme}\" we explore,\nWhere {adjective} wonders lie in store.\nWith {noun} as our faithful guide,\nWe journey to the other side.\n\nThrough {adjective} paths and winding ways,\nWe discover {noun} that never fades.\nA {adjective} tribute to your theme,\nLike poetry from a {adjective} dream."
            ],
            "long": [
                "In contemplation of \"{theme}\" so bright,\nI weave these words with pure delight.\nLet imagination take its course,\nAnd poetry flow from creative source.\n\nThrough metaphor and imagery clear,\nThe essence of your theme draws near.\nWith rhythm, rhyme, and {adjective} emotion,\nI craft this verse like {noun} potion.\n\nIn every line a {noun} lies,\nBeneath the {weather} painted skies.\nMay these words touch your very soul,\nAnd make your spirit feel more whole.\n\nFor in the art of poetry,\nWe find our shared humanity.\nA {adjective} bridge from heart to heart,\nWhere {noun} and beauty never part."
            ]
        }
        
        template = random_gen.choice(custom_templates[length])
        
        # Replace theme placeholder
        template = template.replace('"{theme}"', f'"{theme}"')
        
        # Fill other placeholders
        for category, words in word_banks.items():
            placeholder = "{" + category + "}"
            while placeholder in template:
                template = template.replace(placeholder, random_gen.choice(words), 1)
                
        return template
    
    def is_openai_available(self) -> bool:
        """Check if OpenAI is available and properly configured"""
        return bool(self.client and self.openai_api_key and self._api_key_valid)
    
    async def test_openai_connection(self) -> dict:
        """Test OpenAI API connection and return status"""
        if not self.is_openai_available():
            return {
                "available": False,
                "error": "OpenAI client not properly initialized",
                "details": "No valid API key or client initialization failed"
            }
        
        try:
            # Make a simple test call
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
                timeout=10.0
            )
            
            return {
                "available": True,
                "model": "gpt-3.5-turbo",
                "status": "Connection successful"
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "insufficient_quota" in error_msg:
                return {
                    "available": False,
                    "error": "Quota exceeded",
                    "details": "OpenAI API quota has been exceeded. Please check billing."
                }
            elif "rate limit" in error_msg or "429" in error_msg:
                return {
                    "available": False,
                    "error": "Rate limited",
                    "details": "API rate limit reached. Please try again later."
                }
            elif "authentication" in error_msg or "401" in error_msg:
                return {
                    "available": False,
                    "error": "Authentication failed",
                    "details": "Invalid API key. Please check your OpenAI API key."
                }
            else:
                return {
                    "available": False,
                    "error": "Connection failed",
                    "details": str(e)
                }
    
    def get_service_info(self) -> dict:
        """Get information about the poem service configuration"""
        return {
            "openai_configured": self.is_openai_available(),
            "api_key_present": bool(self.openai_api_key),
            "api_key_valid_format": self._api_key_valid,
            "fallback_available": True,
            "supported_styles": ["creative", "rhyming", "free_verse", "haiku", "sonnet"],
            "supported_lengths": ["short", "medium", "long"]
        }