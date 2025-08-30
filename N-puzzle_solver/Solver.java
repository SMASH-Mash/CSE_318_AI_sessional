import java.util.*;

public class Solver 
{
    private Board initial;
    private Heuristic heuristic;
    private int moves;
    private List<Board> solutionPath = new ArrayList<>();
    private int nodesExplored = 0;
    private int nodesExpanded = 0;

    public Solver(Board initial, Heuristic heuristic) 
    {
        this.initial = initial;
        this.heuristic = heuristic;
    }

    public void solve() 
    {
        PriorityQueue<Node> open = new PriorityQueue<>(Comparator.comparingDouble(n -> n.priority));
        Set<Board> closed = new HashSet<>();

        open.add(new Node(initial, 0, null));
        nodesExplored++;

        while (!open.isEmpty()) 
        {
            Node current = open.poll();

            if (current.board.isGoal()) 
            {
                reconstructPath(current);
                moves = current.moves;
                return;
            }

            closed.add(current.board);
            nodesExpanded++;
            List<Board> neighbors = current.board.neighbors();
            for (Board neighbor : neighbors) 
            {
                if (!closed.contains(neighbor)) 
                {
                    open.add(new Node(neighbor, current.moves + 1, current));
                    nodesExplored++;
                }
            }
        }
    }

    private void reconstructPath(Node node) 
    {
        Stack<Board> stack = new Stack<>();
        while (node != null) 
        {
            stack.push(node.board);
            node = node.previous;
        }
        while (!stack.isEmpty()) 
        {
            solutionPath.add(stack.pop());
        }
    }

    public int getMoves() 
    {
        return moves;
    }

    public List<Board> getSolutionPath() 
    {
        return solutionPath;
    }

    public int getNodesExplored() 
    {
        return nodesExplored;
    }

    public int getNodesExpanded() 
    {
        return nodesExpanded;
    }

    private class Node 
    {
        Board board;
        int moves;
        double priority;
        Node previous;

        public Node(Board board, int moves, Node previous) 
        {
            this.board = board;
            this.moves = moves;
            this.previous = previous;
            this.priority = moves + heuristic.estimate(board);
        }
    }
}