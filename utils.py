from itertools import islice


class Utils:

    @staticmethod
    def chunks_list(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    @staticmethod
    def chunks_dict(data, size):
        it = iter(data)
        for i in range(0, len(data), size):
            yield {k: data[k] for k in islice(it, size)}
