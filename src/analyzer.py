
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter, defaultdict
import spacy
from textstat import flesch_reading_ease, avg_sentence_length
import re
from typing import Dict, List, Tuple

class LinguisticAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words('english'))
        
        # Adicionar stop words corporativas comuns
        self.corporate_stopwords = {
            'email', 'sent', 'subject', 'from', 'to', 'cc', 'bcc',
            'forwarded', 'original', 'message', 'wrote', 'date'
        }
        self.stop_words.update(self.corporate_stopwords)
        
    def analyze_person(self, emails: List[str], person_name: str) -> Dict:
        """Análise completa dos padrões linguísticos de uma pessoa"""
        
        # Juntar todos os emails
        full_text = ' '.join(emails)
        
        analysis = {
            'person': person_name,
            'total_emails': len(emails),
            'comfort_words': self._get_comfort_words(full_text),
            'favorite_phrases': self._get_favorite_phrases(emails),
            'writing_style': self._analyze_writing_style(full_text),
            'vocabulary_diversity': self._calculate_diversity(full_text),
            'linguistic_fingerprint': self._create_fingerprint(emails),
            'email_patterns': self._analyze_email_patterns(emails)
        }
        
        return analysis
    
    def _get_comfort_words(self, text: str, top_n: int = 30) -> List[Tuple[str, int]]:
        """Identifica as palavras mais usadas (excluindo stopwords)"""
        words = word_tokenize(text.lower())
        
        # Filtrar palavras relevantes
        meaningful_words = [
            word for word in words 
            if word.isalpha() 
            and word not in self.stop_words 
            and len(word) > 3
        ]
        
        return Counter(meaningful_words).most_common(top_n)
    
    def _get_favorite_phrases(self, emails: List[str], n_gram: int = 3) -> List[Tuple[str, int]]:
        """Identifica frases/expressões favoritas (bigrams e trigrams)"""
        all_phrases = []
        
        for email in emails:
            words = word_tokenize(email.lower())
            
            # Criar n-grams
            for i in range(len(words) - n_gram + 1):
                phrase = ' '.join(words[i:i + n_gram])
                
                # Filtrar frases com substância
                if all(word not in self.stop_words or word in ['not', 'very', 'really'] 
                       for word in words[i:i + n_gram]):
                    all_phrases.append(phrase)
        
        return Counter(all_phrases).most_common(20)
    
    def _analyze_writing_style(self, text: str) -> Dict:
        """Analisa o estilo de escrita"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        style = {
            'avg_sentence_length': avg_sentence_length(text),
            'reading_ease': flesch_reading_ease(text),
            'exclamation_usage': text.count('!') / len(sentences),
            'question_usage': text.count('?') / len(sentences),
            'uppercase_ratio': sum(1 for w in words if w.isupper()) / len(words),
            'punctuation_style': self._analyze_punctuation(text)
        }
        
        return style
    
    def _calculate_diversity(self, text: str) -> Dict:
        """Calcula métricas de diversidade vocabular"""
        words = word_tokenize(text.lower())
        meaningful_words = [w for w in words if w.isalpha() and w not in self.stop_words]
        
        unique_words = set(meaningful_words)
        
        diversity = {
            'total_words': len(meaningful_words),
            'unique_words': len(unique_words),
            'lexical_diversity': len(unique_words) / len(meaningful_words) if meaningful_words else 0,
            'vocabulary_richness': self._calculate_ttr(meaningful_words)
        }
        
        return diversity
    
    def _calculate_ttr(self, words: List[str]) -> float:
        """Type-Token Ratio para medir riqueza vocabular"""
        if not words:
            return 0
        
        # Calcular TTR em chunks de 1000 palavras (mais estável)
        chunk_size = 1000
        ttrs = []
        
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            if len(chunk) > 100:  # Chunks muito pequenos não são confiáveis
                ttr = len(set(chunk)) / len(chunk)
                ttrs.append(ttr)
        
        return sum(ttrs) / len(ttrs) if ttrs else 0
    
    def _create_fingerprint(self, emails: List[str]) -> Dict:
        """Cria uma 'impressão digital' linguística única"""
        fingerprint = {
            'starter_phrases': self._get_email_starters(emails),
            'closing_phrases': self._get_email_closings(emails),
            'transition_words': self._get_transition_preferences(emails),
            'emphasis_patterns': self._get_emphasis_patterns(emails)
        }
        
        return fingerprint
    
    def _get_email_starters(self, emails: List[str]) -> List[Tuple[str, int]]:
        """Como a pessoa geralmente começa emails"""
        starters = []
        
        for email in emails:
            sentences = sent_tokenize(email)
            if sentences:
                first = sentences[0][:50]  # Primeiros 50 chars
                starters.append(first)
        
        return Counter(starters).most_common(5)
    
    def _get_email_closings(self, emails: List[str]) -> List[Tuple[str, int]]:
        """Como a pessoa geralmente termina emails"""
        closings = []
        
        for email in emails:
            sentences = sent_tokenize(email)
            if sentences:
                last = sentences[-1][-50:]  # Últimos 50 chars
                closings.append(last)
        
        return Counter(closings).most_common(5)
    
    def _get_transition_preferences(self, emails: List[str]) -> Dict:
        """Palavras de transição preferidas"""
        transitions = ['however', 'therefore', 'moreover', 'furthermore',
                      'nevertheless', 'consequently', 'additionally',
                      'meanwhile', 'otherwise', 'accordingly']
        
        text = ' '.join(emails).lower()
        usage = {word: text.count(word) for word in transitions}
        
        return dict(sorted(usage.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def _get_emphasis_patterns(self, emails: List[str]) -> Dict:
        """Como a pessoa enfatiza pontos"""
        patterns = {
            'all_caps': 0,
            'repetition': 0,
            'very_really': 0,
            'absolutely_definitely': 0
        }
        
        for email in emails:
            patterns['all_caps'] += len(re.findall(r'\b[A-Z]{3,}\b', email))
            patterns['very_really'] += email.lower().count('very') + email.lower().count('really')
            patterns['absolutely_definitely'] += email.lower().count('absolutely') + email.lower().count('definitely')
        
        return patterns
    
    def _analyze_email_patterns(self, emails: List[str]) -> Dict:
        """Padrões específicos de email"""
        patterns = {
            'avg_email_length': sum(len(e.split()) for e in emails) / len(emails),
            'greeting_style': self._analyze_greetings(emails),
            'signature_style': self._analyze_signatures(emails)
        }
        
        return patterns
    
    def _analyze_greetings(self, emails: List[str]) -> Dict:
        """Analisa estilos de saudação"""
        greetings = defaultdict(int)
        
        greeting_patterns = [
            (r'^(hi|hello|hey)\s+\w+', 'informal'),
            (r'^(dear|greetings)\s+\w+', 'formal'),
            (r'^(good\s+(morning|afternoon|evening))', 'time_based'),
            (r'^\w+,', 'name_only')
        ]
        
        for email in emails:
            email_lower = email.lower().strip()
            for pattern, style in greeting_patterns:
                if re.match(pattern, email_lower):
                    greetings[style] += 1
                    break
        
        return dict(greetings)
    
    def _analyze_signatures(self, emails: List[str]) -> Dict:
        """Analisa estilos de assinatura"""
        signatures = defaultdict(int)
        
        signature_patterns = [
            (r'(best|regards|sincerely)', 'formal'),
            (r'(thanks|thx|ty)', 'grateful'),
            (r'(cheers|talk soon)', 'casual'),
            (r'^-\s*\w+', 'minimal')
        ]
        
        for email in emails:
            # Pegar últimas linhas
            lines = email.strip().split('\n')
            last_lines = ' '.join(lines[-3:]).lower()
            
            for pattern, style in signature_patterns:
                if re.search(pattern, last_lines):
                    signatures[style] += 1
        
        return dict(signatures)
    
    def _analyze_punctuation(self, text: str) -> Dict:
        """Analisa uso de pontuação"""
        total_chars = len(text)
        
        return {
            'ellipsis_usage': text.count('...') / total_chars * 1000,
            'dash_usage': (text.count('-') + text.count('—')) / total_chars * 1000,
            'parenthesis_usage': text.count('(') / total_chars * 1000,
            'semicolon_usage': text.count(';') / total_chars * 1000
        }