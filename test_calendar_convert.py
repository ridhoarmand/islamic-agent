import asyncio
from services.calendar_service import CalendarService

async def test_convert_to_hijri():
    calendar_service = CalendarService()
    
    # Test konversi tanggal
    print("Testing convert_to_hijri:")
    result = await calendar_service.convert_to_hijri(23, 6, 2024)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        data = result['data']
        print(f"Hari: {data['weekday']['indonesian']}")
        print(f"Hijriah: {data['day']} {data['month']['indonesian']} {data['year']} H")
        print(f"Bulan (nomor): {data['month']['number']}")
    else:
        print(f"Error: {result['message']}")
    
    print("\n-----------------------------------\n")
    
    # Test tanggal Hijriah hari ini
    print("Testing get_hijri_date:")
    result = await calendar_service.get_hijri_date()
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        data = result['data']
        print(f"Hari: {data['weekday']['indonesian']}")
        print(f"Hijriah: {data['day']} {data['month']['indonesian']} {data['year']} H")
        print(f"Bulan (nomor): {data['month']['number']}")
    else:
        print(f"Error: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_convert_to_hijri())
