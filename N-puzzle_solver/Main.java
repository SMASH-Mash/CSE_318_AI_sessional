import java.util.Scanner;

public class Main 
{
    public static void main(String[] args) 
    {
        Scanner scanner = new Scanner(System.in);

        int size = scanner.nextInt();
        int[][] initialBoard = new int[size][size];

        for (int i = 0; i < size; i++)
            for (int j = 0; j < size; j++)
                initialBoard[i][j] = scanner.nextInt();
        String choice=null;
        if(args.length>0)
            choice = args[0];

        Heuristic heuristic;
        if (choice == null || choice.isEmpty()) 
        {
            heuristic = new LinearConflictHeuristic();
        }
        else
        {    
            switch (choice.toLowerCase()) 
            {
                case "manhattan":
                    heuristic = new ManhattanHeuristic();
                    break;
                case "hamming" :
                    heuristic = new HammingHeuristic();
                    break;
                case "euclidean" :
                    heuristic = new EuclideanHeuristic();
                    break;
                case "linear"  :
                    heuristic = new LinearConflictHeuristic();
                    break;
                default :
                    System.out.println("Invalid choice. Defaulting to Manhattan.");
                    heuristic = new LinearConflictHeuristic();
                    break;
            }
        }

        Board initial = new Board(initialBoard);
        if (!initial.isSolvable()) 
        {
            System.out.println("Unsolvable puzzle");
            scanner.close();    
            return;
        }

        Solver solver = new Solver(initial, heuristic);
        solver.solve();

        System.out.println("Minimum number of moves = " + solver.getMoves());
        for (Board board : solver.getSolutionPath()) 
        {
            board.printBoard();
            System.out.println();
        }
        System.out.println("Nodes explored = " + solver.getNodesExplored());
        System.out.println("Nodes expanded = " + solver.getNodesExpanded());
        scanner.close();
    }
}