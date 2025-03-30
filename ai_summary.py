import logging
import re
from collections import Counter
from string import punctuation

# Set up logging
logger = logging.getLogger(__name__)

def generate_ai_summary(query, results, max_results=5):
    """
    Generate a summary of search results using local extractive summarization techniques
    
    Args:
        query (str): The search query
        results (list): List of search result dictionaries
        max_results (int): Maximum number of results to use for the summary
    
    Returns:
        str: Generated summary or None if an error occurs
    """
    try:
        # Use only top results
        used_results = results[:max_results]
        
        if not used_results:
            return None
        
        # Step 1: Collect all text from snippets
        all_text = ""
        for result in used_results:
            if result.get('snippet'):
                all_text += result.get('snippet', '') + " "
        
        # Step 2: Clean text
        all_text = all_text.lower()
        all_text = re.sub(r'\s+', ' ', all_text)  # Replace multiple spaces with single space
        all_text = re.sub(r'[^\w\s]', ' ', all_text)  # Remove punctuation
        
        # Step 3: Extract important keywords from the query and text
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such',
            'can', 'now', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'to', 'at', 'in', 'on',
            'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'from', 'up', 'down', 'of', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'whom', 'who', 'whose', 'with'
        }
        
        # Extract significant words from query
        query_words = [w.lower() for w in query.split() if w.lower() not in stop_words]
        
        # Count word frequencies in the text
        words = [word for word in all_text.split() if word not in stop_words and len(word) > 2]
        word_freq = Counter(words)
        
        # Boost the significance of words that appear in the query
        for word in word_freq:
            if word in query_words or any(query_word in word for query_word in query_words):
                word_freq[word] *= 3
        
        # Step 4: Extract most informative sentences from snippets
        sentences = []
        for result in used_results:
            if result.get('snippet'):
                # Split snippet into sentences (simple approach)
                snippet_sentences = re.split(r'(?<=[.!?])\s+', result.get('snippet', ''))
                for sentence in snippet_sentences:
                    if len(sentence) > 20:  # Ignore very short sentences
                        sentences.append(sentence)
        
        # Step 5: Score sentences based on important words and query relevance
        scored_sentences = []
        for sentence in sentences:
            # Clean the sentence for scoring
            clean_sentence = sentence.lower()
            clean_sentence = re.sub(r'[^\w\s]', ' ', clean_sentence)
            
            # Base score
            score = 0
            
            # Add score for important words
            for word in clean_sentence.split():
                if word in word_freq:
                    score += word_freq[word]
            
            # Add bonus for query terms presence
            for query_word in query_words:
                if query_word in clean_sentence:
                    score += 5
                    
            # Normalize by sentence length (but not too much)
            words_count = len(clean_sentence.split())
            if words_count > 0:
                score = score / (words_count ** 0.5)  # Use square root to avoid over-penalizing longer sentences
            
            scored_sentences.append((sentence, score))
        
        # Step 6: Sort and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select top 2-3 sentences
        num_sentences = min(3, len(scored_sentences))
        top_sentences = [s[0] for s in scored_sentences[:num_sentences]]
        
        # Step 7: Construct the summary
        if top_sentences:
            # Start with the query
            capitalized_query = query.capitalize()
            if not capitalized_query.endswith('?'):
                summary = f"About '{capitalized_query}': "
            else:
                summary = ""
                
            # Add the extracted sentences
            summary += " ".join(top_sentences)
            
            # Clean up the summary (remove extra spaces, fix punctuation)
            summary = re.sub(r'\s+', ' ', summary).strip()
            return summary
        else:
            # Fallback to a simpler extraction if no sentences were scored highly
            titles = [result.get('title', '') for result in used_results if result.get('title')]
            if titles:
                return f"Related to '{query}': {'. '.join(titles[:2])}"
            
        return None
            
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return None