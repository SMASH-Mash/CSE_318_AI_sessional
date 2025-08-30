import java.util.*;
import java.io.*;
import java.util.concurrent.*;

class Example {
    double[] attributes;
    String label;

    public Example(double[] attributes, String label) {
        this.attributes = attributes;
        this.label = label;
    }
}

class TreeNode {
    boolean isLeaf;
    String classLabel;
    int attribute;
    double splitValue;
    TreeNode left;
    TreeNode right;

    public TreeNode(String classLabel) {
        isLeaf = true;
        this.classLabel = classLabel;
    }

    public TreeNode(int attribute, double splitValue) {
        isLeaf = false;
        this.attribute = attribute;
        this.splitValue = splitValue;
        left = null;
        right = null;
    }
}

class DecisionTree {
    String criterion;

    public DecisionTree(String criterion) {
        this.criterion = criterion;
    }

    private double log2(double x) {
        return x == 0 ? 0 : Math.log(x) / Math.log(2);
    }

    private double entropy(List<Example> examples) {
        if (examples.isEmpty()) return 0;
        Map<String, Integer> counts = new HashMap<>();
        for (Example e : examples) {
            counts.put(e.label, counts.getOrDefault(e.label, 0) + 1);
        }
        double entropy = 0;
        int n = examples.size();
        for (int count : counts.values()) {
            double p = (double) count / n;
            entropy -= p * log2(p);
        }
        return entropy;
    }

    private double computeCriterion(List<Example> parent, List<Example> left, List<Example> right, int k) {
        double n = parent.size();
        double nL = left.size();
        double nR = right.size();
        double eP = entropy(parent);
        double eL = entropy(left);
        double eR = entropy(right);
        double ig = eP - (nL / n) * eL - (nR / n) * eR;

        switch (criterion) {
            case "IG":
                return ig;
            case "IGR":
                double iv = 0;
                if (nL > 0) iv -= (nL / n) * log2(nL / n);
                if (nR > 0) iv -= (nR / n) * log2(nR / n);
                return iv == 0 ? 0 : ig / iv;
            case "NWIG":
                double logTerm = log2(k + 1);
                double penalty = 1 - (double) (k - 1) / n;
                return (ig / logTerm) * penalty;
            default:
                throw new IllegalArgumentException("Invalid criterion");
        }
    }

    private boolean allSameClass(List<Example> examples) {
        if (examples.isEmpty()) return true;
        String firstLabel = examples.get(0).label;
        for (Example e : examples) {
            if (!e.label.equals(firstLabel)) return false;
        }
        return true;
    }

    private String majorityClass(List<Example> examples) {
        Map<String, Integer> counts = new HashMap<>();
        for (Example e : examples) {
            counts.put(e.label, counts.getOrDefault(e.label, 0) + 1);
        }
        return Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
    }

    public TreeNode buildTree(List<Example> examples, List<Integer> attrs, int depth, int maxDepth, Map<Integer, Integer> kMap) {
        if (examples.isEmpty()) {
            return new TreeNode("unknown");
        }
        if (allSameClass(examples)) {
            return new TreeNode(examples.get(0).label);
        }
        if (maxDepth > 0 && depth >= maxDepth) {
            return new TreeNode(majorityClass(examples));
        }

        double bestCriterion = Double.NEGATIVE_INFINITY;
        int bestAttr = -1;
        double bestSplit = Double.NaN;
        List<Example> bestLeft = null;
        List<Example> bestRight = null;

        for (int attr : attrs) {
            final int a = attr;
            examples.sort(Comparator.comparingDouble(e -> e.attributes[a]));
            List<Double> splits = new ArrayList<>();
            for (int i = 0; i < examples.size() - 1; i++) {
                if (!examples.get(i).label.equals(examples.get(i + 1).label)) {
                    double split = (examples.get(i).attributes[a] + examples.get(i + 1).attributes[a]) / 2.0;
                    splits.add(split);
                }
            }

            for (double split : splits) {
                List<Example> left = new ArrayList<>();
                List<Example> right = new ArrayList<>();
                for (Example e : examples) {
                    if (e.attributes[a] <= split) left.add(e);
                    else right.add(e);
                }

                if (left.isEmpty() || right.isEmpty()) continue;

                double critVal = computeCriterion(examples, left, right, kMap.get(a));
                if (critVal > bestCriterion) {
                    bestCriterion = critVal;
                    bestAttr = a;
                    bestSplit = split;
                    bestLeft = left;
                    bestRight = right;
                }
            }
        }

        if (bestAttr == -1) {
            return new TreeNode(majorityClass(examples));
        }

        TreeNode node = new TreeNode(bestAttr, bestSplit);
        node.left = buildTree(bestLeft, attrs, depth + 1, maxDepth, kMap);
        node.right = buildTree(bestRight, attrs, depth + 1, maxDepth, kMap);
        return node;
    }

    public String predict(TreeNode node, Example e) {
        if (node.isLeaf) {
            return node.classLabel;
        }
        if (e.attributes[node.attribute] <= node.splitValue) {
            return predict(node.left, e);
        } else {
            return predict(node.right, e);
        }
    }

    public int countNodes(TreeNode node) {
        if (node == null) return 0;
        if (node.isLeaf) return 1;
        return 1 + countNodes(node.left) + countNodes(node.right);
    }

    public int computeDepth(TreeNode node) {
        if (node == null || node.isLeaf) return 0;
        return 1 + Math.max(computeDepth(node.left), computeDepth(node.right));
    }
}

public class Main {
    public static void main(String[] args) {
        if (args.length != 3 && args.length != 2) {
            System.out.println("Usage: java Main <criterion> <maxDepth> <dataset>");
            System.out.println("Or: java Main <criterion> <maxDepth> for full experiment on Iris");
            return;
        }

        List<Example> dataset = new ArrayList<>();
        Map<Integer, Map<String, Integer>> categoricalMaps = new HashMap<>();
        boolean isAdult = false;
        int numFeatures = 4;

        String datasetFile = "Datasets/Iris.csv";
        if (args.length == 3) {
            datasetFile = args[2];
            if (datasetFile.toLowerCase().contains("adult")) isAdult = true;
        }
        List<Integer> attrs ;

        try (BufferedReader br = new BufferedReader(new FileReader(datasetFile))) {
            if (!isAdult) {
                br.readLine();
                String line;
                while ((line = br.readLine()) != null) {
                    String[] parts = line.split(",");
                    double[] attrsArr = new double[4];
                    for (int i = 0; i < 4; i++) {
                        attrsArr[i] = Double.parseDouble(parts[i + 1]);
                    }
                    dataset.add(new Example(attrsArr, parts[5]));
                }
                attrs = Arrays.asList(0, 1, 2, 3);
                numFeatures = 4;
            } 
            else 
            {

                attrs = new ArrayList<>();
                String line;
                List<List<String>> rawData = new ArrayList<>();
                while ((line = br.readLine()) != null) {
                    String[] parts = line.trim().split(",\\s*");
                    if (parts.length != 15) continue;
                    boolean skip = false;
                    for (String s : parts) if (s.equals("?")) skip = true;
                    if (skip) continue;
                    rawData.add(Arrays.asList(parts));
                }
                int[] isCat = {1, 3, 5, 6, 7, 8, 9, 13};
                for (int i : isCat) categoricalMaps.put(i, new HashMap<>());
                for (List<String> row : rawData) {
                    for (int i : isCat) {
                        Map<String, Integer> map = categoricalMaps.get(i);
                        if (!map.containsKey(row.get(i))) {
                            map.put(row.get(i), map.size());
                        }
                    }
                }
                numFeatures = 14;
                for (int i = 0; i < numFeatures; i++) attrs.add(i);
                for (List<String> row : rawData) {
                    double[] attrsArr = new double[numFeatures];
                    for (int i = 0; i < numFeatures; i++) {
                        if (categoricalMaps.containsKey(i)) {
                            attrsArr[i] = categoricalMaps.get(i).get(row.get(i));
                        } else {
                            attrsArr[i] = Double.parseDouble(row.get(i));
                        }
                    }
                    dataset.add(new Example(attrsArr, row.get(14)));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
            return;
        }

        int numRuns = 20;
        int numThreads = Math.min(numRuns, Runtime.getRuntime().availableProcessors());
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);

        if (args.length == 2) {
            String criterion = args[0];
            int maxDepth = Integer.parseInt(args[1]);
            List<Future<Double>> futures = new ArrayList<>();

            for (int run = 0; run < numRuns; run++) {
                final int runId = run;
                futures.add(executor.submit(() -> {
                    List<Example> dataCopy = new ArrayList<>(dataset);
                    Collections.shuffle(dataCopy, new Random(runId));
                    int splitIdx = (int) (0.8 * dataCopy.size());
                    List<Example> train = new ArrayList<>(dataCopy.subList(0, splitIdx));
                    List<Example> test = new ArrayList<>(dataCopy.subList(splitIdx, dataCopy.size()));

                    Map<Integer, Integer> kMap = new HashMap<>();
                    for (int a : attrs) {
                        Set<Double> distinct = new HashSet<>();
                        for (Example e : train) {
                            distinct.add(e.attributes[a]);
                        }
                        kMap.put(a, distinct.size());
                    }

                    DecisionTree tree = new DecisionTree(criterion);
                    TreeNode root = tree.buildTree(train, attrs, 0, maxDepth, kMap);

                    int correct = 0;
                    for (Example e : test) {
                        if (tree.predict(root, e).equals(e.label)) {
                            correct++;
                        }
                    }
                    return (double) correct / test.size();
                }));
            }
            double totalAccuracy = 0;
            for (Future<Double> f : futures) {
                try {
                    totalAccuracy += f.get();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
            executor.shutdown();
            System.out.printf("Average accuracy: %.4f\n", totalAccuracy / numRuns);
        } 
        else {
            String[] criteria = {args[0]};
            int[] maxDepths = new int[1];
            for (int i = 0; i <= 0; i++) maxDepths[i] = Integer.parseInt(args[1]);

            for (String criterion : criteria) {
                for (int maxDepth : maxDepths) {
                    List<Future<double[]>> futures = new ArrayList<>();
                    for (int run = 0; run < numRuns; run++) {
                        final int runId = run;
                        futures.add(executor.submit(() -> {
                            List<Example> dataCopy = new ArrayList<>(dataset);
                            Collections.shuffle(dataCopy, new Random(runId));
                            int splitIdx = (int) (0.8 * dataCopy.size());
                            List<Example> train = new ArrayList<>(dataCopy.subList(0, splitIdx));
                            List<Example> test = new ArrayList<>(dataCopy.subList(splitIdx, dataCopy.size()));

                            Map<Integer, Integer> kMap = new HashMap<>();
                            for (int a : attrs) {
                                Set<Double> distinct = new HashSet<>();
                                for (Example e : train) {
                                    distinct.add(e.attributes[a]);
                                }
                                kMap.put(a, distinct.size());
                            }

                            DecisionTree tree = new DecisionTree(criterion);
                            TreeNode root = tree.buildTree(train, attrs, 0, maxDepth, kMap);

                            int correct = 0;
                            for (Example e : test) {
                                if (tree.predict(root, e).equals(e.label)) {
                                    correct++;
                                }
                            }
                            double accuracy = (double) correct / test.size();
                            double nodes = tree.countNodes(root);
                            double depth = tree.computeDepth(root);
                            return new double[]{accuracy, nodes, depth};
                        }));
                    }
                    double totalAccuracy = 0, totalNodes = 0, totalDepth = 0;
                    System.out.println("All results: ");
                    for (Future<double[]> f : futures) {
                        try {
                            double[] res = f.get();
                            totalAccuracy += res[0];
                            totalNodes += res[1];
                            totalDepth += res[2];
                            System.out.println("Accuracy: " + res[0] + ", Nodes: " + res[1] + ", Depth: " + res[2]);
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    System.out.println("criterion,maxDepth,avgAccuracy,avgNodes,avgDepth");
                    System.out.printf("%s,%d,%.4f,%.1f,%.1f\n",
                        criterion, maxDepth, totalAccuracy / numRuns, totalNodes / numRuns, totalDepth / numRuns);
                    

                }
            }
            executor.shutdown();
        }
    }
}
