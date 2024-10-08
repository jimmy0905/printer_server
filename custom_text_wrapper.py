import textwrap


class CustomTextWrapper(textwrap.TextWrapper):
    def _split(self, text):
        chunks = super()._split(text)
        new_chunks = []
        for chunk in chunks:
            # print(chunk)
            if "\u4e00" <= chunk[0] <= "\u9fff":
                new_chunks.extend(list(chunk))
            else:
                new_chunks.append(chunk)
        return new_chunks

    def _wrap_chunks(self, chunks):
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if chunks:
            cur_line = [chunks.pop(0)]
            cur_len = get_width_of_string(cur_line[0])
        else:
            cur_line = []
            cur_len = 0
        while chunks:
            chunk = chunks.pop(0)
            chunk_width = get_width_of_string(chunk)
            if cur_len + chunk_width <= self.width:
                cur_len += chunk_width
                cur_line.append(chunk)
            else:
                if chunk_width > self.width:
                    # Split the chunk if it's wider than the width
                    split_point = self.width - cur_len
                    cur_line.append(chunk[:split_point])
                    lines.append("".join(cur_line))
                    chunk = chunk[split_point:]
                    while get_width_of_string(chunk) > self.width:
                        lines.append(chunk[:self.width])
                        chunk = chunk[self.width:]
                    cur_line = [chunk]
                    cur_len = get_width_of_string(chunk)
                else:
                    lines.append("".join(cur_line))
                    cur_line = [chunk]
                    cur_len = get_width_of_string(cur_line[0])
        if cur_line:
            lines.append("".join(cur_line))
        return lines


def get_width_of_string(s):
    width = 0
    for character in s:
        if "\u4e00" <= character <= "\u9fff":
            width += 2
        else:
            width += 1
    return width
