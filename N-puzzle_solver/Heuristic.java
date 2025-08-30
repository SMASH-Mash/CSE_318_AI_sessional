public interface Heuristic 
{
    double estimate(Board board);
}
class ManhattanHeuristic implements Heuristic 
{
    int abs(int x) 
    {
        if(x < 0) 
            return -x;  
        return x;
    }
    public double estimate(Board board) 
    {
        int dist = 0;
        int size = board.tiles.length;
        for (int i = 0; i < size; i++) 
        {
            for (int j = 0; j < size; j++) 
            {
                int value = board.tiles[i][j];
                if (value != 0) 
                {
                    int targetRow = (value-1)/size;
                    int targetCol = (value-1)%size;
                    dist += abs(i - targetRow) + abs(j - targetCol);
                }
            }
        }
        return dist;
    }
}

class HammingHeuristic implements Heuristic 
{
    public double estimate(Board board) 
    {
        int count = 0;
        int size = board.tiles.length;
        for (int i = 0; i < size; i++) 
            for (int j = 0; j < size; j++) 
                if (board.tiles[i][j]!=0 && board.tiles[i][j]!=(i*size+j+1))
                    count++;
        return count;
    }
}

class EuclideanHeuristic implements Heuristic 
{
    public double estimate(Board board) 
    {
        double dist = 0;
        int size = board.tiles.length;
        for (int i = 0; i < size; i++) 
        {
            for (int j = 0; j < size; j++) 
            {
                int value = board.tiles[i][j];
                if (value != 0) 
                {
                    int row_number = (value - 1) / size;
                    int colm_number = (value - 1) % size;
                    dist += Math.sqrt((i-row_number)*(i-row_number)+(j-colm_number)*(j-colm_number));
                }
            }
        }
        return dist;
    }
}
class LinearConflictHeuristic implements Heuristic 
{
    public double estimate(Board board) 
    {
        double manhattan = new ManhattanHeuristic().estimate(board);

        return manhattan + 2*(estimate_rows(board) + estimate_cols(board));
    }

    public int estimate_rows(Board board)
    {
        int size = board.tiles.length,conflict=0;
        for (int i = 0; i < size; i++) 
        {
            for (int j = 0; j < size; j++) 
            {
                int value = board.tiles[i][j];
                if (value!=0 && (value-1)/size==i)
                {
                    for (int k = j + 1; k < size; k++) 
                    {
                        int chk = board.tiles[i][k];
                        if (chk != 0 && (chk - 1) / size == i && value > chk) 
                        {
                            conflict++;
                        }
                    }
                }
            }
        }
        return conflict;
    }

    public int estimate_cols(Board board)
    {
        int size = board.tiles.length,conflict=0;
        for (int j = 0; j < size; j++) 
        {
            for (int i = 0; i < size; i++) 
            {
                int value = board.tiles[i][j];
                if (value!=0 && (value-1)%size == j) 
                {
                    for (int k = i + 1; k < size; k++) 
                    {
                        int chk = board.tiles[k][j];
                        if (chk != 0 && (chk - 1) % size == j && value > chk) 
                        {
                            conflict++;
                        }
                    }
                }
            }
        }
        return conflict;
    }
}
