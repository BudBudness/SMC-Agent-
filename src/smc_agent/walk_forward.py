from dataclasses import dataclass

@dataclass
class Window:
    train_start: int
    train_end: int
    test_start: int
    test_end: int

def windows(n, train=500, test=100, step=None):
    step = step or test
    out = []
    i = train
    while i + test <= n:
        out.append(Window(i-train,i,i,i+test))
        i += step
    return out

def walk_forward(data, signal_fn, simulator_factory, train=500, test=100):
    reports = []
    for w in windows(len(data),train,test):
        sim = simulator_factory()
        signals = signal_fn(data[:w.test_start])
        test_bars = data[w.test_start:w.test_end]
        allowed = {b["timestamp"] for b in test_bars}
        signals = [s for s in signals if s.get("timestamp") in allowed]
        sim.run(test_bars, signals)
        reports.append({"window":w.__dict__,"metrics":sim.metrics()})
    return reports
