import time
import funcBot as f

while True:
    f.set_last_chat_id_and_text(f.get_updates())
    time.sleep(0.5)
