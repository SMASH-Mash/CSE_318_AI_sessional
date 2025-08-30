import java.util.*;

public class Board 
{
    public int[][] tiles;
    private int size;
    private int blankRow, blankCol;

    public Board(int[][] grid) 
    {
        this.size = grid.length;
        tiles = new int[size][size];
        for (int i = 0; i < size; i++) 
        {
            for (int j = 0; j < size; j++) 
            {
                tiles[i][j] = grid[i][j];
                if (tiles[i][j] == 0) 
                {
                    blankRow = i;
                    blankCol = j;
                }
            }
        }
    }

    public boolean isGoal() 
    {
        int value = 1;
        for (int i = 0; i < size; i++) 
        {
            for (int j = 0; j < size; j++) 
            {
                if (i == size - 1 && j == size - 1) 
                {
                    if (tiles[i][j] != 0) 
                        return false;
                } 
                else if (tiles[i][j] != value) 
                {   
                    return false;
                }
                value++;
            }
        }
        return true;
    }

    public List<Board> neighbors() 
    {
        List<Board> neighbors = new ArrayList<>();
        int[] dx = { -1, 1, 0, 0 };
        int[] dy = { 0, 0, -1, 1 };

        for (int dir = 0; dir < 4; dir++) {
            int row_num = blankRow + dx[dir];
            int colm_num = blankCol + dy[dir];

            if (inBounds(row_num, colm_num)) {
                int[][] copy = copyTiles();
                swap(copy, blankRow, blankCol, row_num, colm_num);
                neighbors.add(new Board(copy));
            }
        }

        return neighbors;
    }

    public boolean isSolvable() {
        int[] arr = new int[size * size];
        int idx = 0;
        for (int[] row : tiles)
            for (int tile : row)
                arr[idx++] = tile;

        int inversions = 0;
        for (int i = 0; i < arr.length; i++) {
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[i] > arr[j] && arr[i] != 0 && arr[j] != 0)
                    inversions++;
            }
        }

        if (size % 2 == 1)
            return inversions % 2 == 0;
        else {
            int blankRowFromBottom = size - blankRow;
            return (blankRowFromBottom % 2 == 0) != (inversions % 2 == 0);
        }
    }

    private boolean inBounds(int r, int c) {
        return r >= 0 && r < size && c >= 0 && c < size;
    }

    private int[][] copyTiles() {
        int[][] copy = new int[size][size];
        for (int i = 0; i < size; i++)
            copy[i] = tiles[i].clone();
        return copy;
    }

    private void swap(int[][] array, int r1, int c1, int r2, int c2) {
        int temp = array[r1][c1];
        array[r1][c1] = array[r2][c2];
        array[r2][c2] = temp;
    }

    public void printBoard() {
        for (int[] row : tiles) {
            for (int tile : row) {
                System.out.print(tile + " ");
            }
            System.out.println();
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Board)) return false;
        Board board = (Board) o;
        return Arrays.deepEquals(tiles, board.tiles);
    }

    @Override
    public int hashCode() {
        return Arrays.deepHashCode(tiles);
    }
}