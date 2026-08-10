import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.otp_verification import OTPVerification
from app.models.user import User


class AuthService:

    @staticmethod
    async def send_otp(db: AsyncSession, mobile: str):

        otp = str(random.randint(100000, 999999))

        otp_record = OTPVerification(
            id=str(uuid.uuid4()),
            mobile=mobile,
            otp=otp,
            verified=False,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
        )

        db.add(otp_record)
        await db.commit()

        # TODO: Integrate SMS provider later
        print(f"OTP for {mobile}: {otp}")

        return {
            "message": "OTP sent successfully"
        }

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        mobile: str,
        otp: str
    ):

        result = await db.execute(
            select(OTPVerification)
            .where(
                OTPVerification.mobile == mobile,
                OTPVerification.otp == otp,
                OTPVerification.verified == False
            )
        )

        otp_record = result.scalar_one_or_none()

        if otp_record is None:
            raise Exception("Invalid OTP")

        if otp_record.expires_at < datetime.utcnow():
            raise Exception("OTP expired")

        otp_record.verified = True

        result = await db.execute(
            select(User)
            .where(User.mobile == mobile)
        )

        user = result.scalar_one_or_none()

        if user is None:

            user = User(
                id=str(uuid.uuid4()),
                mobile=mobile,
                name="New Student",
                role="student",
                login_provider="mobile",
                is_mobile_verified=True,
            )

            db.add(user)

        else:
            user.is_mobile_verified = True

        await db.commit()

        return user