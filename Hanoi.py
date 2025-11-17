import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QBrush, QColor

class Disc(QGraphicsRectItem):
    def __init__(self, size, width, height, color):
        super().__init__(0, 0, width, height)
        self.size = size
        self.setBrush(QBrush(color))
        self.setZValue(size)  # Larger discs go behind smaller ones

class HanoiVisualizer(QGraphicsView):
    def __init__(self, num_discs=3):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedSize(600, 400)
        self.scene.setSceneRect(0, 0, 600, 400)

        self.num_discs = num_discs
        self.pegs = { 'A': [], 'B': [], 'C': [] }
        self.peg_positions = { 'A': 100, 'B': 300, 'C': 500 }
        self.disc_height = 20
        self.peg_base_y = 350

        self.move_generator = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_move)

        self.init_discs()
        # Initialize generator instead of pre-computing all moves
        self.move_generator = self.solve_hanoi(self.num_discs, 'A', 'B', 'C')
        self.timer.start(1000)

    def init_discs(self):
        for i in range(self.num_discs, 0, -1):
            width = 30 + i * 20
            disc = Disc(i, width, self.disc_height, QColor(100 + i*30, 100, 255 - i*30))
            self.scene.addItem(disc)
            self.pegs['A'].append(disc)
            self.place_disc(disc, 'A', len(self.pegs['A']) - 1)

    def place_disc(self, disc, peg, position):
        x = self.peg_positions[peg] - disc.rect().width() / 2
        y = self.peg_base_y - position * self.disc_height
        disc.setPos(x, y)

    def solve_hanoi(self, n, source, auxiliary, target):
        """Generator that yields moves one at a time instead of storing all moves."""
        if n == 1:
            yield (source, target)
        else:
            yield from self.solve_hanoi(n - 1, source, target, auxiliary)
            yield (source, target)
            yield from self.solve_hanoi(n - 1, auxiliary, source, target)

    def next_move(self):
        try:
            source, target = next(self.move_generator)
            disc = self.pegs[source].pop()
            self.pegs[target].append(disc)
            self.place_disc(disc, target, len(self.pegs[target]) - 1)
        except StopIteration:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HanoiVisualizer(num_discs=4)
    window.show()
    sys.exit(app.exec_())
