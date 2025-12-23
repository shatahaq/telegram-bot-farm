import time
import random
import asyncio
from google import genai
from google.genai import types
from telethon import TelegramClient

# ==================== KONFIGURASI UTAMA ====================
API_KEY_GEMINI = "AIzaSyD4rHC4-6dBJ8gAj5W4t448I-qdr_9DMwM"
GROUP_ID = -1003671105521 

# Daftar 5 Akun Telegram (Session sudah tersimpan di folder)
ACCOUNTS = [
    {"session": "session_akun_1", "api_id": 38335934, "api_hash": "6485d169fe03c2b67296d010714ef5f7", "persona": "Budi: Tech enthusiast, santai, pakai bahasa gaul Jaksel."},
    {"session": "session_akun_2", "api_id": 39334769, "api_hash": "dad6128722a21b0d4dee78082c361f8b", "persona": "Santi: Mahasiswi kritis, suka nanya detail, bahasa sehari-hari."},
    {"session": "session_akun_3", "api_id": 39133003, "api_hash": "5f8bfd0e5d954dd7ab8ea1978dd6bbeb", "persona": "Andi: Pekerja kantoran, suka kasih opini singkat, sering typo."},
    {"session": "session_akun_4", "api_id": 35367538, "api_hash": "a7e772bacf21f41d319174ea17f4d10d", "persona": "Citra: Expert di bidang crypto/web3, bahasa rapi tapi gak kaku."},
    {"session": "session_akun_5", "api_id": 34968573, "api_hash": "01305dc60b7800c1afa44d1b0983cc9c", "persona": "Eko: Orang awam yang penasaran, suka nimbrung, ceplas-ceplos."}
]

# Inisialisasi Google Gen AI Client
client_ai = genai.Client(api_key=API_KEY_GEMINI)

# ===========================================================

async def get_ai_response(history, persona):
    """Meminta jawaban dari AI dengan retry logic untuk menghindari Error 429"""
    prompt = f"""
    Kamu adalah {persona}. Kita lagi seru-seruan diskusi di Grup Telegram "Komunitas Crypto Indonesia".
    Topik: Bitcoin, Altcoin, Web3, Future Trading, FOMO, FUD, dan market analysis yang lagi hype.
    
    Chat history terakhir:
    {history}
    
    TUGAS: Respon chat terakhir sebagai sesama member grup yang antusias.
    
    STRICT RULES (PENTING):
    1. **Panjang Respon**: WAJIB antara 50 sampai 100 kata. Jangan kependekan, jangan kepanjangan.
    2. **Gaya Bahasa**: WAJIB Gaul, Santai, pake bahasa tongkrongan (lu, gue, anjir, gokil, hold, seroook, to the moon, sangkut). 
    3. **Human-Like**: 
       - Gunakan singkatan chat sehari-hari (yg, gk, bgt, pdhl, krn).
       - Buat senatural mungkin, boleh ada typo dikit (misal: "btcoin", "etherium").
       - JANGAN kaku, JANGAN pake bahasa robot/formal/baku.
       - Hindari penggunaan list/numbering jika bisa diceritakan dalam paragraf.
       - Gunakan emosi (senang, panik, santuy).
       - **PENTING**: Selesaikan kalimat dengan tanda baca, jangan kepotong!
    4. **Topik**: Selalu kaitkan sama kondisi market crypto, koin micin, atau fundamental project.
    5. **Forbidden**: JANGAN pernah bilang "Sebagai AI", "Mesin", atau bahasa normatif. Lo itu trader/investor crypto!
    """

    for attempt in range(3):  # Coba maksimal 3 kali jika gagal
        try:
            response = client_ai.models.generate_content(
                model='gemini-flash-latest', # Model paling stabil untuk Free Tier
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=1.2, # Stabil agar tidak kepotong
                    top_p=0.95,
                    max_output_tokens=8192,
                )
            )
            return response.text
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 30
                print(f"!! Limit API (429) tercapai. Menunggu {wait_time} detik...")
                await asyncio.sleep(wait_time)
            else:
                print(f"!! Gagal generate AI: {e}")
                break
    
    return "Gila sih, bahasannya makin seru aja. Gue ampe bingung mau nambahin apa lagi, tapi poin tadi masuk akal juga sih."

async def start_automation():
    clients = []
    # Load session yang sudah ada (tidak perlu login ulang)
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc['session'], acc['api_id'], acc['api_hash'])
            await client.start()
            clients.append({
                "client": client, 
                "persona": acc['persona'], 
                "name": acc['session']
            })
            print(f"Berhasil Load: {acc['session']}")
        except Exception as e:
            print(f"Gagal Load {acc['session']}: {e}")

    print("\n--- SISTEM OTOMATISASI AKTIF ---")
    last_speaker_name = None

    while True:
        # 1. Pastikan akun yang berbeda yang membalas (Rotasi)
        available_clients = [c for c in clients if c['name'] != last_speaker_name]
        current = random.choice(available_clients)
        client = current['client']
        last_speaker_name = current['name']

        print(f"\n[{current['name']}] Sedang menyiapkan balasan...")

        try:
            # 2. Ambil konteks chat agar nyambung
            history = ""
            async for msg in client.iter_messages(GROUP_ID, limit=10):
                if msg.text:
                    history += f"User_{msg.sender_id}: {msg.text}\n"

            # 3. Generate Jawaban AI
            reply_text = await get_ai_response(history, current['persona'])

            # 4. Simulasi Membaca & Mengetik
            await client.send_read_acknowledge(GROUP_ID)
            async with client.action(GROUP_ID, 'typing'):
                # Mengetik selama 15-25 detik
                await asyncio.sleep(random.randint(15, 25))

            # 5. Kirim Pesan
            await client.send_message(GROUP_ID, reply_text)
            print(f"[{current['name']}] Berhasil kirim pesan.")

        except Exception as e:
            print(f"!! Error saat proses chat: {e}")

        # 6. Jeda antar chat (8 - 12 menit)
        sleep_duration = random.randint(480, 720)
        print(f"Sistem standby. Chat berikutnya dalam {sleep_duration/60:.1f} menit.")
        await asyncio.sleep(sleep_duration)

if __name__ == '__main__':
    try:
        asyncio.run(start_automation())
    except KeyboardInterrupt:
        print("\nSistem dihentikan manual.")