# juego/agente_conexion.py
from collections import deque
import heapq

from AgenteIA.Agente import Agente


class AgenteConexion(Agente):
    """
    Agente que conecta una emoción con su estación.
    Implementa BFS (amplitud), DFS (profundidad) y UCS (costouniforme).

    - historial_busqueda: lista de celdas visitadas en orden (para animación).
    """

    def __init__(self, tablero):
        super().__init__()
        self.tablero = tablero
        self.historial_busqueda = []

    def get_costo(self, camino):
        """Costo total del camino (suma de costos de entrar a cada celda, sin contar la inicial)."""
        if not camino:
            return 0
        return sum(c.get_costo() for c in camino[1:])

    def buscar(self, inicio, meta, tecnica="amplitud"):
        self.historial_busqueda = []

        if tecnica == "profundidad":
            return self._dfs(inicio, meta)
        if tecnica == "costouniforme":
            return self._ucs(inicio, meta)
        # default: BFS
        return self._bfs(inicio, meta)

    # -----------------------
    # Helpers
    # -----------------------
    def _reconstruir(self, came_from, start, goal):
        if goal not in came_from and goal != start:
            return []
        cur = goal
        path = [cur]
        while cur != start:
            cur = came_from[cur]
            path.append(cur)
        path.reverse()
        return path

    def _vecinos(self, celda):
        return self.tablero.get_vecinos(celda.q, celda.r)

    # -----------------------
    # BFS
    # -----------------------
    def _bfs(self, start, goal):
        q = deque([start])
        came = {}
        visited = {start}

        while q:
            cur = q.popleft()
            self.historial_busqueda.append(cur)

            if cur == goal:
                return self._reconstruir(came, start, cur)

            for nb in self._vecinos(cur):
                if nb not in visited:
                    visited.add(nb)
                    came[nb] = cur
                    q.append(nb)
        return []

    # -----------------------
    # DFS
    # -----------------------
    def _dfs(self, start, goal):
        stack = [start]
        came = {}
        visited = set()

        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            self.historial_busqueda.append(cur)

            if cur == goal:
                return self._reconstruir(came, start, cur)

            # orden reversible para que “se sienta” DFS
            vecinos = list(self._vecinos(cur))[::-1]
            for nb in vecinos:
                if nb not in visited:
                    if nb not in came:  # guarda padre la primera vez
                        came[nb] = cur
                    stack.append(nb)
        return []

    # -----------------------
    # Uniform Cost Search (UCS)
    # -----------------------
    def _ucs(self, start, goal):
        pq = [(0, start)]
        came = {}
        best = {start: 0}
        closed = set()

        while pq:
            g, cur = heapq.heappop(pq)
            if cur in closed:
                continue
            closed.add(cur)
            self.historial_busqueda.append(cur)

            if cur == goal:
                return self._reconstruir(came, start, cur)

            for nb in self._vecinos(cur):
                ng = g + nb.get_costo()
                if nb not in best or ng < best[nb]:
                    best[nb] = ng
                    came[nb] = cur
                    heapq.heappush(pq, (ng, nb))
        return []