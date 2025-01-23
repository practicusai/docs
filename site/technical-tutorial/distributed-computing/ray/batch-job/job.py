import practicuscore as prt

ray = prt.distributed.get_client()


@ray.remote
def square(x):
    return x * x


def calculate():
    numbers = [i for i in range(10)]
    futures = [square.remote(i) for i in numbers]
    results = ray.get(futures)
    print("Distributed square results of", numbers, "is", results)


if __name__ == "__main__":
    calculate()
    ray.shutdown()
