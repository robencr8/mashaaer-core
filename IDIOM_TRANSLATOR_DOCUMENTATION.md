# Multilingual Emotion Idiom Translator

The Mashaaer Feelings application now includes a Multilingual Emotion Idiom Translator that allows users to translate emotional expressions and idioms between Arabic and English, while preserving cultural context and emotional meaning.

## Features

1. **Idiom Translation**: Translate emotional idioms between Arabic and English with preserved meaning
2. **Cultural Context**: Get explanations of idioms' cultural significance
3. **Common Idioms**: Discover common emotional expressions in each supported language
4. **Emotion-Based Filtering**: Find idioms related to specific emotions

## API Endpoints

### 1. Get Supported Languages

Get a list of languages supported by the idiom translator.

**Request**:
```
GET /api/idioms/languages
```

**Response**:
```json
{
  "success": true,
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "ar", "name": "Arabic"}
  ]
}
```

### 2. Get Common Emotional Idioms

Get a list of common emotional idioms for a specific language, optionally filtered by emotion.

**Request**:
```
GET /api/idioms/common?language=en&emotion=happy
```

Query parameters:
- `language`: Language code (required, e.g., "en" or "ar")
- `emotion`: Specific emotion to filter by (optional, e.g., "happy", "sad", "angry")

**Response**:
```json
{
  "success": true,
  "language": "en",
  "emotion": "happy",
  "idioms": [
    {
      "idiom": "Walking on sunshine",
      "meaning": "Feeling extremely happy and carefree",
      "emotion": "happy"
    },
    // More idioms...
  ]
}
```

### 3. Translate Idiom

Translate an emotional idiom or expression from one language to another.

**Request**:
```
POST /api/idioms/translate
```

Body:
```json
{
  "idiom": "Walking on sunshine",
  "source_lang": "en",
  "target_lang": "ar",
  "emotion": "happy",
  "provide_explanation": true
}
```

Parameters:
- `idiom`: The idiom or expression to translate (required)
- `source_lang`: Source language code (required, e.g., "en" or "ar")
- `target_lang`: Target language code (required, e.g., "en" or "ar")
- `emotion`: The emotion expressed by the idiom (optional, helps with accurate translation)
- `provide_explanation`: Whether to include cultural context explanation (optional, defaults to false)

**Response**:
```json
{
  "success": true,
  "original_idiom": "Walking on sunshine",
  "translated_idiom": "طاير من الفرحة",
  "source_language": "en",
  "target_language": "ar",
  "emotional_meaning": "Feeling extremely happy and carefree",
  "literal_meaning": "Flying from happiness",
  "cultural_context": "In Arabic culture, the imagery of flying is often associated with extreme happiness and freedom from worries"
}
```

## Examples

### Example 1: Translating "Walking on sunshine" to Arabic

```bash
curl -X POST http://localhost:5000/api/idioms/translate \
  -H "Content-Type: application/json" \
  -d '{
    "idiom": "Walking on sunshine",
    "source_lang": "en",
    "target_lang": "ar",
    "emotion": "happy",
    "provide_explanation": true
  }'
```

### Example 2: Getting common sad idioms in Arabic

```bash
curl "http://localhost:5000/api/idioms/common?language=ar&emotion=sad"
```

## Integration with Other Features

The Idiom Translator integrates well with the emotion analysis capabilities of Mashaaer Feelings. After detecting an emotion in a user's text, you can suggest idioms related to that emotion in either language.

## Technical Notes

- The translator uses AI language models to provide culturally appropriate translations
- Mock data is used as a fallback when the AI service is unavailable
- All translations are cached to improve performance and reduce API calls
- The feature supports additional languages in the future (currently only Arabic and English)