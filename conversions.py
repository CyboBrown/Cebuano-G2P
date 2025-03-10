import pandas as pd
import re
import unicodedata

def normalize(s):
    # Use regex to match words or single punctuation marks
    result = s.lower()
    result = result.replace("e", "i")
    result = result.replace("é", "í")
    result = result.replace("o", "u")
    result = result.replace("ó", "ú")
    return result

def split_into_tokens(s):
    # Use regex to match words (including hyphenated ones) or single punctuation marks
    tokens = re.findall(r"\b[\w']+(?:-[\w']+)*\b|[^\w\s]", s)
    cleaned_tokens = [token.replace("'", "") for token in tokens]
    return cleaned_tokens

## Add exceptions for "mga" and numbers

def phonemize_exceptions(tokens):
    exceptions0 = ["ang", "kang", "ni", "nga", "sa", "si", "ug", "ra", "ka"]
    exceptions1 = ["ba", "lang", "na", "pa"]
    def phonemize(token):
        if token in exceptions0 or token in exceptions1:
            token = token.replace("ng", "ŋ")
            if token[0] in ["a", "i", "u", "á", "í", "ú"]:
                token = "q" + token
            # if token in exceptions1:
            #     return token + "1"
            # return token + "0"
        return token
    tokens = map(phonemize, tokens)
    return tokens

def match_words_with_dataset(tokens):
    # Load the CSV file into a DataFrame
    file_path = "data/ceb_roots_phonemic.csv"
    df = pd.read_csv(file_path)
    # Filter rows where the search_column matches the target word
    def match_to_dataset(token):
        filtered_rows = df[df["normalized_head"] == token]
        if len(filtered_rows) == 0:
            return token
        return filtered_rows["head"].tolist()[0]
    tokens = map(match_to_dataset, tokens)
    return tokens

def phonemize_closed_penult(tokens):
    def replace_dash_to_q(s):
        return s.replace("-", "q")

    def insert_q_between_vowels(s):
        vowels = "aeiouAEIOUáéíóúÁÉÍÓÚ"
        result = []  # Store modified characters
        for i in range(len(s)):
            result.append(s[i])
            # If the current character is a vowel and the next one is also a vowel, insert "q"
            if s[i] in vowels and (i + 1 < len(s) and s[i + 1] in vowels):
                result.append("q")  
        return "".join(result)

    def add_stress_if_closed_penult(token):
        vowels = "aeiou"
        stressed_vowels = {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú"}
        
        # Function to check if a character is a consonant
        def is_consonant(char):
            return char.isalpha() and char not in vowels

        # Skip if token is already stressed or does not need stress
        if token[-1] in ["*", ".", ","] or any(char in "áéíóú" for char in token or sum(1 for char in token if char in "aeiouáéíóúAEIOUÁÉÍÓÚ") == 1):
            return token
        
        token = token.replace("ng", "ŋ")
        # Find the last vowel and its position
        last_vowel_match = re.search(r"[aeiou](?!.*[aeiou])", token) # Match the last vowel
        if not last_vowel_match:
            return token # If no vowels, return the word as is
        last_vowel_index = last_vowel_match.start()
        # Check consonants before the last vowel
        consonant_count = 0
        for i in range(last_vowel_index - 1, -1, -1):  # Iterate backwards before the last vowel
            if is_consonant(token[i]):
                consonant_count += 1
            else:
                break  # Stop counting consonants at the previous vowel or non-consonant
        # Determine where to apply stress
        if consonant_count >= 2:  # Closed syllable
            # Add stress to the penultimate vowel
            for i in range(last_vowel_index - 1, -1, -1):
                if token[i] in stressed_vowels:
                    return token[:i] + stressed_vowels[token[i]] + token[i + 1:]
        else:  # Open syllable
            # Add stress to the penultimate vowel
            for i in range(last_vowel_index - 1, -1, -1):
                if token[i] in stressed_vowels:
                    return token[:i] + stressed_vowels[token[i]] + token[i + 1:]
            # return token[:last_vowel_index] + stressed_vowels[token[last_vowel_index]] + token[last_vowel_index + 1:] # If add stress to last vowel
        
        return token  # Return unchanged if no stress could be applied
    
    tokens = map(replace_dash_to_q, tokens)
    tokens = map(insert_q_between_vowels, tokens)
    tokens = map(add_stress_if_closed_penult, tokens)
    return tokens


def convert(input):
    text = normalize(input)
    tokens = split_into_tokens(text)
    # tokens = phonemize_exceptions(tokens)
    tokens = match_words_with_dataset(tokens)
    tokens = phonemize_closed_penult(tokens)
    return tokens

def convert_ipa(tokens):
    syllable_regex = re.compile(r"[^aeiouáéíóú]*[aeiouáéíóú]+(?:[^aeiouáéíóú]*$|[^aeiouáéíóú](?=[^aeiouáéíóú]))?", re.IGNORECASE)
    def syllabify(tokens):
        result = []
        for token in tokens:
            syllables = syllable_regex.findall(token)
            result.extend(syllables)  # Add syllables
            result.append(" ")  # Add space after each word
        if result:  
            result.pop()  # Remove the trailing space
        return result
    syllabicated = syllabify(tokens)
    char_map = {
        "q": "ʔ", "r": "4", "y": "j", "u": "ʊ",
        "á": "a", "é": "ɛ", "í": "i", "ó": "o", "ú": "ʊ"
    }
    def map_characters(words_list):
        mapped_words = []
        for word in words_list:
            contains_stressed = any(char in "áéíóú" for char in word)
            mapped_word = "".join(char_map.get(char, char) for char in word)
            if contains_stressed:
                mapped_word = "ˈ" + mapped_word
            mapped_words.append(mapped_word)
        return mapped_words
    return "".join(map_characters(syllabicated))

def synthesize_text(text, phonetic_text):
    """Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    text = text.replace("e", "i")
    text = text.replace("o", "u")
    # phonetic_text = "gika\"?Un sa ?i\"4U? ?aN bU\"kUg"
    print(text)
    print(phonetic_text)
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(ssml="\u003cspeak\u003e\r\n    \u003cphoneme alphabet\u003d\"ipa\" ph\u003d\u0027" + phonetic_text + "\u0027\u003e\r\n    " + text + "\r\n    \u003c/phoneme\u003e\r\n\u003c/speak\u003e")

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="fil-PH",
        name="fil-PH-Standard-D"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')