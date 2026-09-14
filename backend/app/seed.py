from sqlalchemy import select

import app.db  # noqa: F401
from app.db.base import Base
from app.db.models.crop_profile import CropProfile
from app.db.models.crop_requirement import CropRequirement
from app.db.models.field import Field
from app.db.models.field_context_snapshot import FieldContextSnapshot
from app.db.models.sensor_device import SensorDevice
from app.db.session import engine

REGIONS_DATA = [
    ("MMR001", "Sagaing Region", "စစ်ကိုင်းတိုင်းဒေသကြီး"),
    ("MMR002", "Bago Region", "ပဲခူးတိုင်းဒေသကြီး"),
    ("MMR003", "Magway Region", "မကွေးတိုင်းဒေသကြီး"),
    ("MMR004", "Mandalay Region", "မန္တလေးတိုင်းဒေသကြီး"),
    ("MMR005", "Tanintharyi Region", "တနင်္သာရီတိုင်းဒေသကြီး"),
    ("MMR006", "Ayeyarwady Region", "ဧရာဝတီတိုင်းဒေသကြီး"),
    ("MMR007", "Kachin State", "ကချင်ပြည်နယ်"),
    ("MMR008", "Kayah State", "ကယားပြည်နယ်"),
    ("MMR009", "Kayin State", "ကရင်ပြည်နယ်"),
    ("MMR010", "Chin State", "ချင်းပြည်နယ်"),
    ("MMR011", "Mon State", "မွန်ပြည်နယ်"),
    ("MMR012", "Rakhine State", "ရခိုင်ပြည်နယ်"),
    ("MMR013", "Shan State (North)", "ရှမ်းပြည်နယ် (မြောက်ပိုင်း)"),
    ("MMR014", "Yangon Region", "ရန်ကုန်တိုင်းဒေသကြီး"),
    ("MMR015", "Nay Pyi Taw", "နေပြည်တော်"),
    ("MMR016", "Shan State (South)", "ရှမ်းပြည်နယ် (တောင်ပိုင်း)"),
    ("MMR017", "Shan State (East)", "ရှမ်းပြည်နယ် (အရှေ့ပိုင်း)"),
    ("MMR018", "Bago Region (East)", "ပဲခူးတိုင်းဒေသကြီး (အရှေ့ပိုင်း)"),
]


async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.db.session import session_factory
    async with session_factory() as session:
        existing = await session.execute(select(CropProfile).limit(1))
        if existing.scalar_one_or_none():
            return

        from app.db.models.region import Region
        for pcode, name_en, name_my in REGIONS_DATA:
            session.add(Region(pcode=pcode, name_en=name_en, name_my=name_my))

        maize = CropProfile(
            name="Maize",
            description="Maize (Zea mays) general agronomic requirements for tropical varieties.",
            source="FAO Ecocrop / Myanmar Agriculture Department",
            source_url="https://ecocrop.fao.org",
        )
        session.add(maize)
        await session.flush()

        req_list = [
            ("temperature", 18, 35, "°C", "critical"),
            ("soil_moisture", 40, 80, "%", "important"),
            ("ph", 5.5, 7.5, "pH", "critical"),
            ("light", 60, 100, "%", "important"),
            ("rainfall", 500, 1500, "mm", "advisory"),
            ("humidity", 40, 85, "%", "advisory"),
        ]
        requirements = [
            CropRequirement(
                crop_profile_id=maize.id, factor=f, min_value=mn,
                max_value=mx, unit=u, criticality=c,
            )
            for f, mn, mx, u, c in req_list
        ]
        for req in requirements:
            session.add(req)

        demo_field = Field(
            name="Pyinmana Demo Plot",
            latitude=19.75,
            longitude=96.13,
            region_code="MMR015",
        )
        session.add(demo_field)
        await session.flush()

        context = FieldContextSnapshot(
            field_id=demo_field.id,
            soil_moisture=55.0,
            ph=6.2,
            temperature=28.5,
            humidity=70.0,
            light=85.0,
            rainfall=1100.0,
        )
        session.add(context)

        device = SensorDevice(
            field_id=demo_field.id,
            name="Demo Wokwi Device",
            transport_type="wokwi",
            device_id="wokwi-demo-device",
            is_simulated=True,
        )
        session.add(device)

        await session.commit()
