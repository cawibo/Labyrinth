// marksamman's maze solver

package main

import (
	"container/heap"
	"fmt"
)

const (
	N    = 1
	E    = 2
	W    = 4
	S    = 8
	D    = 16
	U    = 32
	Goal = 64
)

/*

maze := []int{
	{E|D,		W|E|S|D,	W|D,	D,		E|S|D,		W},
	{D,			N|E|S|D,	W,		E,		N|W|E|S,	W},
	{S,			N|E|S,		W|E,	W|S,	N,			S},
	{N|E|S|D,	W|N|S|D,	S,		N,		E,			W|N|D},
	{N|D}
}
*/
var maze [][][]int

var mazeColors = []string{
	`BBBBB0
	BB0000
	000000
	BB000B
	B00B0B
	BBBB0B`,

	`GYYYG0
	YYBB0B
	000B00
	GGB00Y
	G00G0Y
	GYGY0Y`,

	`G0B0Y0
	00YYBY
	0B0YBB
	GYG0B0
	G00YB0
	Y0GB0B`,

	`G0G00B
	B00BGB
	BYB0YG
	YBY0GB
	GB00Y0
	00YY0G`,

	`G0Y0BY
	Y0BYGG
	Y0G0BY
	BY00GG
	GY0000
	0B00BG`,

	`Y000Y0
	00Y0YY
	00Y0Y0
	Y000YY
	Y00000
	0Y00YY`,
}

var mazeStrings = []string{
	`╞╦╡¤╔╡
	¤╠╡╞╬╡
	╥╠═╗╨╥
	╠╣╥╨╞╝
	╨╠╩═╡¤
	¤╨¤╞╡¤`,

	`╥¤╔╦╡╥
	║¤╨║╞╝
	╚╡╞╣╥╥
	¤╞╗╚╬╝
	╔╡║¤╨╥
	╨¤╚══╝`,

	`╥╥╥╥╞╡
	║╠╣╚═╡
	╨╨╨¤¤¤
	¤¤╞╡¤╥
	╞╡╥¤╔╝
	╞╡╨¤╨¤`,

	`╔╡¤╥╥¤
	╠═╡╠╣╥
	╨╥╥╨╠╝
	¤╨╨╔╝¤
	╔╡╥╚╗╥
	╨╞╩╡╚╝`,

	`¤╞╡╥╞╡
	¤╥¤╨╥¤
	¤╚╗╥╨¤
	¤¤╨╚╦╗
	╥¤╔╡║╨
	╚═╝╞╝¤`,

	`╔╡╞╦╦╡
	╨╞═╝╨¤
	╔╡╔╗╞╡
	║╥╨╨¤╥
	╚╩═╦╡╨
	╞═╡╨¤E`,
}

type Node struct {
	Step string
	Prev *Node

	MazeIdx int
	Col     int
	Row     int

	index    int
	priority int
}

// A PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	// We want Pop to give us the highest, not lowest, priority so we use greater than here.
	return pq[i].priority <= pq[j].priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Node)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

func main() {
	for _, mazeString := range mazeStrings {
		var level [][]int
		var levelRow []int
		for _, n := range mazeString {
			if n == '\t' {
				continue
			}
			if n == '\n' {
				level = append(level, levelRow)
				levelRow = []int{}
				continue
			}

			var flags int
			if n == '╞' {
				flags = E
			} else if n == '╡' {
				flags = W
			} else if n == '╦' {
				flags = W | E | S
			} else if n == '¤' {
				// only up/down, judge by color
			} else if n == '╔' {
				flags = S | E
			} else if n == '╠' {
				flags = N | E | S
			} else if n == '╬' {
				flags = N | E | W | S
			} else if n == '╥' {
				flags = S
			} else if n == '═' {
				flags = W | E
			} else if n == '╗' {
				flags = W | S
			} else if n == '╨' {
				flags = N
			} else if n == '╣' {
				flags = W | N | S
			} else if n == '╝' {
				flags = W | N
			} else if n == '╩' {
				flags = W | N | E
			} else if n == '║' {
				flags = N | S
			} else if n == '╚' {
				flags = N | E
			} else if n == 'E' {
				flags = Goal
			} else {
				fmt.Printf("UNHANDLED SYMBOL: %c (%d)\n", n, n)
			}
			levelRow = append(levelRow, flags)
		}
		level = append(level, levelRow)
		maze = append(maze, level)
	}

	var mazeIdx int
	for _, mazeColor := range mazeColors {
		var col, row int
		for _, c := range mazeColor {
			if c == '\t' {
				continue
			} else if c == '\n' {
				row++
				col = 0
				continue
			}

			flags := maze[mazeIdx][row][col]
			if c == 'G' {
				flags |= U | D
			} else if c == 'Y' {
				flags |= U
			} else if c == 'B' {
				flags |= D
			} else if c == '0' {
				// nothing
			} else {
				fmt.Printf("UNHANDLED COLOR: %c (%d)\n", c, c)
			}

			maze[mazeIdx][row][col] = flags

			col++
		}
		mazeIdx++
	}

	pq := make(PriorityQueue, 1)
	pq[0] = &Node{
		Step: "start",
		Prev: nil,

		MazeIdx: 0,
		Col:     1,
		Row:     1,

		index:    0,
		priority: 0,
	}
	heap.Init(&pq)

	visited := make(map[string]struct{})

	for pq.Len() > 0 {
		n := heap.Pop(&pq).(*Node)

		idx := fmt.Sprintf("%d,%d,%d", n.MazeIdx, n.Row, n.Col)
		if _, ok := visited[idx]; ok {
			continue
		}
		visited[idx] = struct{}{}

		flags := maze[n.MazeIdx][n.Row][n.Col]
		if (flags & Goal) != 0 {
			fmt.Println(n.Step)
			break
		}

		if (flags & N) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " north",
				Prev: n,

				MazeIdx:  n.MazeIdx,
				Col:      n.Col,
				Row:      n.Row - 1,
				priority: n.priority + 1,
			})
		}
		if (flags & E) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " east",
				Prev: n,

				MazeIdx:  n.MazeIdx,
				Col:      n.Col + 1,
				Row:      n.Row,
				priority: n.priority + 1,
			})
		}
		if (flags & W) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " west",
				Prev: n,

				MazeIdx:  n.MazeIdx,
				Col:      n.Col - 1,
				Row:      n.Row,
				priority: n.priority + 1,
			})
		}
		if (flags & S) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " south",
				Prev: n,

				MazeIdx:  n.MazeIdx,
				Col:      n.Col,
				Row:      n.Row + 1,
				priority: n.priority + 1,
			})
		}
		if (flags & D) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " down",
				Prev: n,

				MazeIdx:  n.MazeIdx + 1,
				Col:      n.Col,
				Row:      n.Row,
				priority: n.priority + 1,
			})
		}
		if (flags & U) != 0 {
			heap.Push(&pq, &Node{
				Step: n.Step + " up",
				Prev: n,

				MazeIdx:  n.MazeIdx - 1,
				Col:      n.Col,
				Row:      n.Row,
				priority: n.priority + 1,
			})
		}
	}
}
