"""연락처 관리 도구 모듈

업무 연락처를 관리하고 자동으로 연락처 정보를 추출하여 저장합니다.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from src.models.database import Contact, SessionLocal
from src.models.schemas import ContactOut


class ContactTool:
    """연락처 관리 도구

    텍스트에서 연락처 정보를 추출하고 관리합니다.
    """

    def __init__(self):
        pass

    async def extract_and_save_contact(self, analyzed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """텍스트에서 연락처 정보를 추출하고 저장"""
        persons = analyzed_data.get("entities", {}).get("persons", [])
        text = analyzed_data.get("original_text", "")
        
        if not persons:
            return None
            
        # 여러 이메일/전화번호 추출
        contact_data = self._extract_contact_info(text, persons[0])
        
        # 중복 체크: 이름+이메일(들) 기준
        emails = contact_data.get("emails", [])
        db: Session = SessionLocal()
        query = db.query(Contact).filter(Contact.name == persons[0])
        if emails:
            for email in emails:
                if email:
                    query = query.filter(Contact.emails.like(f"%{email}%"))
        existing_contact = query.first()
        db.close()
        if existing_contact:
            return ContactOut.from_orm(existing_contact).dict()
        
        # 새로운 연락처 저장
        return await self._save_contact(contact_data)

    async def _find_contact_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """이름으로 연락처 검색"""
        db: Session = SessionLocal()
        contact = db.query(Contact).filter(Contact.name == name).first()
        db.close()
        
        if contact:
            return ContactOut.from_orm(contact).dict()
        return None

    def _extract_contact_info(self, text: str, name: str) -> Dict[str, Any]:
        import re
        # 여러 이메일 추출
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        # 여러 전화번호 추출
        phone_patterns = [
            r'\d{3}-\d{3,4}-\d{4}',
            r'\d{2,3}-\d{3,4}-\d{4}',
            r'\d{10,11}'
        ]
        phones = []
        for pattern in phone_patterns:
            phones += re.findall(pattern, text)
        phones = list(set(phones))
        contact_info = {
            "name": name,
            "email": emails[0] if emails else None,  # deprecated
            "phone": phones[0] if phones else None,  # deprecated
            "emails": emails if emails else [],
            "phones": phones if phones else [],
            "company": None,
            "position": None,
            "department": None,
            "notes": f"자동 추출: {text}",
            "user_id": "default"
        }
        # 회사/직책 추출 등 기존 로직 유지
        # ... (생략, 기존 코드 유지)
        # 회사명 추출 (개선된 로직)
        company_patterns = [
            r'([가-힣A-Za-z0-9]+회사)',
            r'([가-힣A-Za-z0-9]+기업)',
            r'([가-힣A-Za-z0-9]+corporation)',
            r'([가-힣A-Za-z0-9]+inc)',
            r'([가-힣A-Za-z0-9]+ltd)',
            r'([가-힣A-Za-z0-9]+co)',
        ]
        for pattern in company_patterns:
            company_match = re.search(pattern, text, re.IGNORECASE)
            if company_match:
                contact_info["company"] = company_match.group(1)
                break
        # 직책 추출 (개선된 로직)
        position_patterns = [
            r'([가-힣]+대표)',
            r'([가-힣]+팀장)',
            r'([가-힣]+부장)',
            r'([가-힣]+과장)',
            r'([가-힣]+사원)',
            r'([가-힣]+매니저)',
            r'(director)',
            r'(manager)',
        ]
        for pattern in position_patterns:
            position_match = re.search(pattern, text, re.IGNORECASE)
            if position_match:
                contact_info["position"] = position_match.group(1)
                break
        return contact_info

    async def _save_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        db: Session = SessionLocal()
        # emails, phones는 쉼표로 join해서 저장
        contact_data["emails"] = ",".join(contact_data.get("emails", []))
        contact_data["phones"] = ",".join(contact_data.get("phones", []))
        contact = Contact(**contact_data)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        db.close()
        # 반환 시 emails, phones는 리스트로 변환
        result = ContactOut.from_orm(contact).dict()
        result["emails"] = contact_data["emails"].split(",") if contact_data["emails"] else []
        result["phones"] = contact_data["phones"].split(",") if contact_data["phones"] else []
        return result

    async def get_contacts(self) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        contacts = db.query(Contact).order_by(Contact.name).all()
        result = []
        for c in contacts:
            d = ContactOut.from_orm(c).dict()
            d["emails"] = c.emails.split(",") if c.emails else []
            d["phones"] = c.phones.split(",") if c.phones else []
            result.append(d)
        db.close()
        return result

    async def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        contacts = db.query(Contact).filter(
            Contact.name.contains(query) | 
            Contact.emails.contains(query) | 
            Contact.company.contains(query)
        ).all()
        result = []
        for c in contacts:
            d = ContactOut.from_orm(c).dict()
            d["emails"] = c.emails.split(",") if c.emails else []
            d["phones"] = c.phones.split(",") if c.phones else []
            result.append(d)
        db.close()
        return result 