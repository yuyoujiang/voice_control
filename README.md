
Terminal1:
```bash
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
python app.py
```
Terminal2:
```bash
cd /home/nvidia/whisper_stable/whisper.cpp
./build/bin/whisper-stream -m ./models/ggml-base.en-q5_1.bin -t 8 --step 0 --length 7000 -vth 0.7 --keep 1200
```

