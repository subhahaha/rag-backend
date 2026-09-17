from app.services.retrieval_service import RetrievalService
from app.llm.client import (
    generate_response,
    extract_booking_details,
    detect_booking_intent,
)
from app.services.chat_memory import (
    get_messages,
    save_message,
    save_booking_field,
    get_booking_data,
    clear_booking_data,
)


from app.services.booking_service import create_booking
from app.schemas.booking import BookingCreate
from database import SessionLocal



class RAGService:
    def __init__(self) -> None:
        self.retrieval_service = RetrievalService()

    def save_booking_turn(
        self,
        conversation_id: str,
        question: str,
        answer: str,
    ) -> str:
        save_message(
            conversation_id,
            "user",
            question,
        )

        save_message(
            conversation_id,
            "assistant",
            answer,
        )

        return answer
    
    def handle_booking(
        self,
        conversation_id: str,
        question: str,
    ) -> str:

        extracted = extract_booking_details(question)

        for field in ["name", "email", "date", "time"]:
            value = extracted.get(field)

            if value:
                save_booking_field(
                    conversation_id,
                    field,
                    value,
                )

        booking_data = get_booking_data(conversation_id)

        if "name" not in booking_data:
            return self.save_booking_turn(
                conversation_id,
                question,
                "What is your name?",
            )

        if "email" not in booking_data:
            return self.save_booking_turn(
                conversation_id,
                question,
                "What is your email address?",
            )

        if "date" not in booking_data:
            return self.save_booking_turn(
                conversation_id,
                question,
                "What date would you like to schedule the interview?",
            )

        if "time" not in booking_data:
            return self.save_booking_turn(
                conversation_id,
                question,
                "What time would you prefer?",
            )

        
        booking = BookingCreate(
            name=booking_data["name"],
            email=booking_data["email"],
            date=booking_data["date"],
            time=booking_data["time"],
        )

        db = SessionLocal()

        try:
            create_booking(
                db=db,
                booking=booking,
            )
        finally:
            db.close()

        clear_booking_data(conversation_id)

        return self.save_booking_turn(
            conversation_id,
            question,
            "Thank you! Your interview has been booked successfully.",
        )

    def answer(self,conversation_id: str,question: str,) -> str:

        booking_data = get_booking_data(conversation_id)

        if booking_data or detect_booking_intent(question):
            return self.handle_booking(
                conversation_id=conversation_id,
                question=question,
            )
        history = get_messages(conversation_id)

        results = self.retrieval_service.retrieve(
            query=question,
            limit=5,
        )

        context = "\n\n".join(
            result["text"]
            for result in results
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Answer the user's question using the provided context "
                    "and conversation history. "
                    "If the answer is not available in the context, "
                    "say you do not have enough information."
                ),
            },
        ]

        for message in history:
            role, content = message.split(": ", 1)

            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                ),
            }
        )

        
        answer = generate_response(messages)

        save_message(
            conversation_id,
            "user",
            question,
        )

        save_message(
            conversation_id,
            "assistant",
            answer,
        )

        return answer