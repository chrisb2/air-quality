"""2.9 inch E-Paper display buffer writing."""
import hershey


class Display:
    """2.9 inch E-Paper display buffer writing."""

    WHITE = 255
    BLACK = 0

    PEN_THIN = 0
    PEN_MEDIUM = 1
    PEN_THICK = 2

    def __init__(self, width, height):
        """Construct buffer writer with width and height of Waveshare."""
        self.w = width
        self.h = height

    def background(self, frame, col):
        """Set background."""
        for i in range(0, 16 * self.h):
            frame[i] = col

    def plot(self, frame, x, y, col):
        """Plot point."""
        tx = y
        ty = x

        if (x < 0) or (x >= self.h) or (y < 0) or (y >= self.w):
            return
        if col == self.WHITE:
            frame[int((tx+ty*self.w)/8)] |= (0x80 >> (tx % 8))
        elif col == self.BLACK:
            frame[int((tx+ty*self.w)/8)] &= ~(0x80 >> (tx % 8))

    def line(self, frame, x, y, x2, y2, col, weight):
        """Draw line."""
        if x > x2:
            dx = x - x2
        else:
            dx = x2 - x
        if y > y2:
            dy = y - y2
        else:
            dy = y2 - y

        if x < x2:
            sx = 1
        else:
            sx = -1

        if y < y2:
            sy = 1
        else:
            sy = -1

        err = dx - dy

        while True:
            self.plot(frame, x, y, col)
            if weight == self.PEN_MEDIUM:
                if self.h-1 >= x+1:
                    self.plot(frame, x+1, y, col)
                if 0 <= x-1:
                    self.plot(frame, x-1, y, col)
                if self.w-1 >= y+1:
                    self.plot(frame, x, y+1, col)
                if 0 <= y-1:
                    self.plot(frame, x, y-1, col)
            elif weight == self.PEN_THICK:
                self.blob(frame, x, y, col)

            if (x == x2) and (y == y2):
                break
            e2 = 2*err
            if e2 > -dy:
                err = err-dy
                x = x+sx
            if (x == x2) and (y == y2):
                self.plot(frame, x, y, col)
                if weight == self.PEN_MEDIUM:
                        if self.h-1 >= x+1:
                            self.plot(frame, x+1, y, col)
                        if 0 <= x-1:
                            self.plot(frame, x-1, y, col)
                        if self.w-1 >= y+1:
                            self.plot(frame, x, y+1, col)
                        if 0 <= y-1:
                            self.plot(frame, x, y-1, col)
                elif weight == self.PEN_THICK:
                    self.blob(frame, x, y, col)
                break

            if e2 < dx:
                err = err+dx
                y = y+sy

    def blob(self, frame, x, y, col):
        """Draw blob."""
        self.line(frame, x-1, y+2,  x+1, y+2, col, self.PEN_THIN)
        self.line(frame, x-2, y+1,  x+2, y+1, col, self.PEN_THIN)
        self.line(frame, x-2, y,  x+2, y, col, self.PEN_THIN)
        self.line(frame, x-2, y-1,  x+2, y-1, col, self.PEN_THIN)
        self.line(frame, x-1, y-2,  x+1, y-2, col, self.PEN_THIN)

    def write_text(self, frame, text, x, y, col, xscale, yscale, dy, weight):
        """Write text."""
        old = False
        do_scale = False
        not_finished = True
        ci = 0
        mdy = 0
        ox = 0
        oy = 0
        wt = 0

        if (xscale > 1.01) or (xscale < 1.01) or \
           (yscale > 1.01) or (yscale < 1.01):
            do_scale = True

        xx = x
        while not_finished:
            if ci == len(text):
                break
            c = ord(text[ci])
            ci += 1
            if (c > 126) or (c < 32):
                continue
            c = c-32
            nv = hershey.simplex[c][0]
            w = hershey.simplex[c][1]
            if w < 0:
                w = 0-w
            if nv == 0:
                xx = xx+w
                wt = wt+w
                continue
            im = 2+(nv*2)
            old = False

            for i in range(2, im, 2):
                ipx = hershey.simplex[c][i]
                ipy = hershey.simplex[c][i+1]
                if ipx >= 0:
                    px = ipx
                else:
                    px = 0-ipx
                if ipy >= 0:
                    py = ipy
                else:
                    if py == -1:
                        py = 32767
                    else:
                        py = 0+ipy

                if do_scale:
                    px = int(float(px)*xscale)
                    py = int(float(py)*yscale)
                if (py != 32767) and (py > mdy):
                    mdy = py+1
                if (ipx == -1) and (ipy == -1):  # pen up
                    old = False
                else:
                    if old:  # a previous point is stored in ox, oy
                        if ((ox+xx) > (self.h-1)) or ((px+xx) > (self.h-1)):
                            not_finished = False
                            break
                        self.line(frame, ox+xx, oy+y, px+xx, py+y, col, weight)
                        ox = px
                        oy = py
                    else:
                        ox = px
                        oy = py
                        old = True
            if do_scale:
                xx = xx+int(float(w)*xscale)
                wt = wt+int(float(w)*xscale)
            else:
                xx = xx+w
                wt = wt+w

        # TODO *dy
        # if dy is not None:
        #     *dy = mdy

        return wt+1
