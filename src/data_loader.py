import pandas as pd
import email
from email.parser import Parser
import os
import json
from typing import Dict, List, Tuple
import re

class EnronDataLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.emails_df = None
        
    def load_emails_from_csv(self, limit: int = None) -> pd.DataFrame:
        """Carrega emails do CSV do Kaggle"""
        print("📧 Carregando emails do Enron dataset...")
        
        # Se você baixou o dataset do Kaggle, ele vem como CSV
        df = pd.read_csv(os.path.join(self.data_path, 'emails.csv'))
        
        if limit:
            df = df.head(limit)
            print(f"✅ Carregados {limit} emails para desenvolvimento rápido")
        
        # Limpar e processar
        df['content'] = df['message'].apply(self._extract_email_body)
        df['sender'] = df['message'].apply(self._extract_sender)
        df['subject'] = df['message'].apply(self._extract_subject)
        
        # Filtrar emails vazios ou muito curtos
        df = df[df['content'].str.len() > 100]
        
        self.emails_df = df
        print(f"✅ {len(df)} emails prontos para análise!")
        
        return df
    
    def _extract_email_body(self, raw_email: str) -> str:
        """Extrai apenas o corpo do email"""
        try:
            # Encontrar onde o corpo começa (após headers)
            lines = raw_email.split('\n')
            body_start = 0
            
            for i, line in enumerate(lines):
                if line.strip() == '':  # Linha vazia separa headers do corpo
                    body_start = i + 1
                    break
            
            body = '\n'.join(lines[body_start:])
            
            # Limpar assinaturas comuns
            body = re.sub(r'-{3,}.*', '', body, flags=re.DOTALL)
            body = re.sub(r'={3,}.*', '', body, flags=re.DOTALL)
            
            return body.strip()
        except:
            return ""
    
    def _extract_sender(self, raw_email: str) -> str:
        """Extrai o remetente do email"""
        match = re.search(r'From:\s*([^\n]+)', raw_email)
        return match.group(1).strip() if match else "Unknown"
    
    def _extract_subject(self, raw_email: str) -> str:
        """Extrai o assunto do email"""
        match = re.search(r'Subject:\s*([^\n]+)', raw_email)
        return match.group(1).strip() if match else "No Subject"
    
    def get_emails_by_person(self, min_emails: int = 50) -> Dict[str, List[str]]:
        """Agrupa emails por pessoa (mínimo de emails para análise significativa)"""
        person_emails = {}
        
        for sender in self.emails_df['sender'].value_counts().index:
            sender_emails = self.emails_df[self.emails_df['sender'] == sender]['content'].tolist()
            
            if len(sender_emails) >= min_emails:
                person_emails[sender] = sender_emails
        
        print(f"✅ Encontradas {len(person_emails)} pessoas com {min_emails}+ emails")
        return person_emails