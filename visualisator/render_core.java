import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.List;
import java.util.ArrayList;
import java.awt.geom.*;
import java.awt.image.BufferedImage;
import java.util.Arrays;
import java.util.Random;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;


public class render_core implements KeyListener{
	public int x_view_angle = 0;
    public int y_view_angle = 0;
    public double zoom = 1.0;
    public int currentMapMode = 1; //Possible are 0,1,2,3,4,5,6,7,8,9 - ten total

    JPanel renderPanel = new JPanel();
    ArrayList<Shape> shapes;
    JTextField tf = new JTextField("../simulation/temp_saves/save2_1");
    double [][] colors_old = new double[1620][15];

	public void keyReleased(KeyEvent e){}
	public void keyTyped(KeyEvent e){}
	public void keyPressed(KeyEvent e){
		int key = e.getKeyCode();
        double move_value = 5/zoom;
		if (key == 37){
			x_view_angle += move_value;

			if (x_view_angle >= 360){
				x_view_angle -= 360;
			}
			renderPanel.repaint();
		}

		if (key == 39){
			x_view_angle -= move_value;
			
			if (x_view_angle <= 0){
				x_view_angle += 360;
			}
			renderPanel.repaint();
		}
		
		if (key == 40){
			y_view_angle += move_value;
			if (y_view_angle >= 360){
				y_view_angle -= 360;
			}
			renderPanel.repaint();
		}

		if (key == 38){
			y_view_angle -= move_value;
			if (y_view_angle <= 0){
				y_view_angle += 360;
			}
			renderPanel.repaint();
		}

        if (key == 45){
            zoom /= 1.1;
            renderPanel.repaint();
        }
        if (key == 61){
            zoom *= 1.1;
            renderPanel.repaint();
        }
	}

	public static void main(String[] args){
		render_core rc = new render_core();
		rc.start();
	}

    public void start() {
        JFrame frame = new JFrame();
        frame.addKeyListener(this);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();

        Container pane = frame.getContentPane();
        pane.setLayout(null);

        renderPanel = new JPanel() {
            public void paintComponent(Graphics g) {
                shapes = new ArrayList<>();
                Graphics2D g2 = (Graphics2D) g;

                load();

                g2.setColor(Color.BLACK);
                g2.fillRect(0, 0, getWidth(), getHeight());

                double heading = Math.toRadians(x_view_angle);
                Matrix3 headingTransform = new Matrix3(new double[]{
                        Math.cos(heading), 0, -Math.sin(heading),
                        0, 1, 0,
                        Math.sin(heading), 0, Math.cos(heading)
                });

                double pitch = Math.toRadians(y_view_angle);
                Matrix3 pitchTransform = new Matrix3(new double[]{
                        1, 0, 0,
                        0, Math.cos(pitch), Math.sin(pitch),
                        0, -Math.sin(pitch), Math.cos(pitch)
                });
                Matrix3 transform = headingTransform.multiply(pitchTransform);

                BufferedImage img = new BufferedImage(getWidth(), getHeight(), BufferedImage.TYPE_INT_ARGB);
                double[] zBuffer = new double[img.getWidth() * img.getHeight()];
                Arrays.fill(zBuffer, Double.NEGATIVE_INFINITY);
                int counter = -1;
                for (Shape shape : shapes) {
                    counter+=1;
                    List<Vertex> transformedVertices = new ArrayList<>();
                    for (Vertex v : shape.sides) {
                        //System.out.println(v.x + " " + v.y + " " + v.z);
                        Vertex tv = transform.transform(v);
                        tv.x *= zoom;
                        tv.y *= zoom;
                        tv.z *= zoom;
                        tv.x += getWidth() / 2;
                        tv.y += getHeight() / 2;
                        transformedVertices.add(tv);
                    }

                    //System.out.println(transformedVertices.get(0).x + " " + transformedVertices.get(0).y + " " + transformedVertices.get(0).z);
                    List<Triangle> triangles = triangulatePolygon(transformedVertices, counter);

                    for (Triangle t : triangles) {
                        renderTriangle(t, img, zBuffer);
                    }
                }
                g2.drawImage(img, 0, 0, null);
            }
        };
        renderPanel.setBounds(0, 0, screenSize.width*2/3, screenSize.height*4/5);  // Using setBounds() for manual positioning
        pane.add(renderPanel);

        JPanel wrapperPanel = new JPanel();
        wrapperPanel.setLayout(null);  // Set to null layout to use setBounds
        wrapperPanel.setBounds(0, 0, screenSize.width, screenSize.height);  // Position wrapperPanel below renderPanel
        

        JLabel label = new JLabel("                                  Controls");
        label.setForeground(Color.BLUE);
        label.setFont(new Font("Arial", Font.BOLD, 20));
        label.setOpaque(true);
        label.setBackground(Color.LIGHT_GRAY);
        label.setBounds(screenSize.width*2/3, 0, screenSize.width/3, screenSize.height/10);


        //Defenition moved to start = new JTextField("save_dir");
        tf.setBounds(screenSize.width*2/3, screenSize.height/10+10, screenSize.width/3, screenSize.height/10-50);
        tf.setFocusable(false);

        tf.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (tf.hasFocus()) {
                    tf.setFocusable(false);           
                    tf.transferFocus();             
                    tf.setFocusable(true);             
                } else {
                    tf.setFocusable(true);
                    tf.requestFocusInWindow();
                }
            }
        });

        tf.addFocusListener(new FocusAdapter() {
            @Override
            public void focusLost(FocusEvent e) {
                frame.requestFocusInWindow(); 
            }
        });

        JTextField tf1 = new JTextField("Logger. After switching mapmode, click any arrow key to update");
        tf1.setBounds(screenSize.width*2/3, screenSize.height/3 + 150, screenSize.width/3, screenSize.height*1/3+50);
        tf1.setFocusable(false);

        /*
        tf1.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (tf.hasFocus()) {
                    tf.setFocusable(false);           
                    tf.transferFocus();             
                    tf.setFocusable(true);             
                } else {
                    tf.setFocusable(true);
                    tf.requestFocusInWindow();
                }
            }
        });

        tf1.addFocusListener(new FocusAdapter() {
            @Override
            public void focusLost(FocusEvent e) {
                frame.requestFocusInWindow(); 
            }
        });
        */

        JLabel label1 = new JLabel("                  Load (if controlls lost focus click text field again)");
        label1.setForeground(new Color(220,220,220));
        label1.setFont(new Font("Arial", Font.BOLD, 15));
        label1.setOpaque(true);
        label1.setBackground(new Color(30,100,30));
        label1.setBounds(screenSize.width*2/3, screenSize.height/10+50, screenSize.width/3, screenSize.height/10);


        JLabel label2 = new JLabel("                                                     Logger");
        label2.setForeground(new Color(220,220,220));
        label2.setFont(new Font("Arial", Font.BOLD, 15));
        label2.setOpaque(true);
        label2.setBackground(new Color(50,50,10));
        label2.setBounds(screenSize.width*2/3, screenSize.height/3, screenSize.width/3, screenSize.height/10);

        JLabel map_mode1 = new JLabel("    Mapmodes");
        map_mode1.setForeground(new Color(50,50,50));
        map_mode1.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode1.setOpaque(true);
        map_mode1.setBackground(new Color(40,100,200));
        map_mode1.setBounds(screenSize.height/10 * 0 + 0, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode2 = new JLabel("    Basic");
        map_mode2.setForeground(new Color(50,50,50));
        map_mode2.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode2.setOpaque(true);
        map_mode2.setBackground(new Color(100,100,100));
        map_mode2.setBounds(screenSize.height/10 * 1 + 7, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode3 = new JLabel("    Complexity");
        map_mode3.setForeground(new Color(50,50,50));
        map_mode3.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode3.setOpaque(true);
        map_mode3.setBackground(new Color(200,100,70));
        map_mode3.setBounds(screenSize.height/10 * 2 + 14, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode4 = new JLabel("    Agressiveness");
        map_mode4.setForeground(new Color(50,50,50));
        map_mode4.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode4.setOpaque(true);
        map_mode4.setBackground(new Color(140,100,200));
        map_mode4.setBounds(screenSize.height/10 * 3 + 20, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode5 = new JLabel("    Devmapmod");
        map_mode5.setForeground(new Color(50,50,50));
        map_mode5.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode5.setOpaque(true);
        map_mode5.setBackground(new Color(140,60,100));
        map_mode5.setBounds(screenSize.height/10 * 4 + 27, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode6 = new JLabel("    Fertility");
        map_mode6.setForeground(new Color(50,50,50));
        map_mode6.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode6.setOpaque(true);
        map_mode6.setBackground(new Color(140,100,20));
        map_mode6.setBounds(screenSize.height/10 * 5 + 34, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode7 = new JLabel("    Rigidness");
        map_mode7.setForeground(new Color(50,50,50));
        map_mode7.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode7.setOpaque(true);
        map_mode7.setBackground(new Color(80,120,120));
        map_mode7.setBounds(screenSize.height/10 * 6 + 40, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode8 = new JLabel("    Speed");
        map_mode8.setForeground(new Color(50,50,50));
        map_mode8.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode8.setOpaque(true);
        map_mode8.setBackground(new Color(100,100,200));
        map_mode8.setBounds(screenSize.height/10 * 7 + 47, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode9 = new JLabel("    Energy cost");
        map_mode9.setForeground(new Color(50,50,50));
        map_mode9.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode9.setOpaque(true);
        map_mode9.setBackground(new Color(100,170,100));
        map_mode9.setBounds(screenSize.height/10 * 8 + 54, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        JLabel map_mode10 = new JLabel("    Energy storage");
        map_mode10.setForeground(new Color(50,50,50));
        map_mode10.setFont(new Font("Arial", Font.BOLD, 12));
        map_mode10.setOpaque(true);
        map_mode10.setBackground(new Color(100,190,200));
        map_mode10.setBounds(screenSize.height/10 * 9 + 60, screenSize.height - screenSize.height/5 + 1, screenSize.height/10, screenSize.height/10);

        map_mode1.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 0;
            }
        });

        map_mode2.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 1;
            }
        });

        map_mode3.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 2;
            }
        });

        map_mode4.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 3;
            }
        });

        map_mode5.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 4;
            }
        });

        map_mode6.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 5;
            }
        });

        map_mode7.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 6;
            }
        });

        map_mode8.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 7;
            }
        });

        map_mode9.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 8;
            }
        });


        map_mode10.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                currentMapMode = 9;
            }
        });

        label1.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                load();
            }
        });

        wrapperPanel.add(map_mode1);
        wrapperPanel.add(map_mode2);
        wrapperPanel.add(map_mode3);
        wrapperPanel.add(map_mode4);
        wrapperPanel.add(map_mode5);
        wrapperPanel.add(map_mode6);
        wrapperPanel.add(map_mode7);
        wrapperPanel.add(map_mode8);
        wrapperPanel.add(map_mode9);
        wrapperPanel.add(map_mode10);

        wrapperPanel.add(label);
        wrapperPanel.add(label1);
        wrapperPanel.add(label2);
        wrapperPanel.add(tf);
        wrapperPanel.add(tf1);

        pane.add(wrapperPanel);

        frame.setSize(screenSize.width, screenSize.height);
        frame.setVisible(true);
    }

    private List<Triangle> triangulatePolygon(List<Vertex> vertices, int pos) {
        Color[] colors = {
            Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW,
            Color.CYAN, Color.MAGENTA, Color.ORANGE, Color.PINK,
            Color.LIGHT_GRAY, Color.GRAY, Color.DARK_GRAY, Color.BLACK
        };

        Random random = new Random();
        Color choice = colors[random.nextInt(colors.length)];
        
        List<Triangle> triangles = new ArrayList<>();
        for (int i = 1; i < vertices.size()-1; i++) {
            //System.out.println(0+ "|" + i + "|" + (i+1));
            //
            triangles.add(new Triangle(vertices.get(0), vertices.get(i), vertices.get(i + 1), determineColor(pos)));
        }
        return triangles;
    }

    private Color determineColor(int pos){
        if (currentMapMode == 0){
            return new Color(80,80,80); //empty
        }
        else if (currentMapMode == 1){
            if (colors_old[pos][0] == 1){
                return new Color(110,210,110);
            } else {
                return new Color(80,80,80);
            }
        }
        
        else if (currentMapMode == 2){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][1] - 5.2) / (5.5 - 5.2) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(100,t,100);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 3){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][2] - 5.2) / (5.9 - 5.2) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(50,50,t);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 4){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][3] - 0) / (1 - 0) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(t,200,200);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 5){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][4] - 5.5) / (6.5 - 5.5) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(100,t,170);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 6){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][5] - 5.5) / (6.5 - 5.5) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(100,t,170);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 7){
            if (colors_old[pos][0] == 1){ //Still same check creature must be present
                int t = (int) ( (colors_old[pos][6] - 5.5) / (6.5 - 5.5) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(170,t,100);
            } else {
                return new Color(80,80,80);
            }
        }

        else if (currentMapMode == 8){
            if (colors_old[pos][0] == 1){ 
                int t = (int) ( (colors_old[pos][7] - 5.5) / (6.5 - 5.5) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(120,100,t);
            } else {
                return new Color(80,80,80);
            }
        }


        else if (currentMapMode == 9){
            if (colors_old[pos][0] == 1){ //Could have used 4 loop, but for that we would have needed mapmode to save file collumn correspondance list defined, which howver might be subject to change later.
                int t = (int) ( (colors_old[pos][8] - 0) / (6 - 0) * 255 );
                if (t > 255){
                    t = 255;
                }
                if (t < 0){
                    t = 0;
                }
                return new Color(t,130,80);
            } else {
                return new Color(80,80,80);
            }
        }


        //Something wrong
        return new Color(180,80,80);
    }

    private void renderTriangle(Triangle t, BufferedImage img, double[] zBuffer) {
        Vertex v1 = t.v1, v2 = t.v2, v3 = t.v3;
        //System.out.println(v1.x + " " + v1.y + " " + v1.z);
        int minX = (int) Math.max(0, Math.ceil(Math.min(v1.x, Math.min(v2.x, v3.x))));
        int maxX = (int) Math.min(img.getWidth() - 1, Math.floor(Math.max(v1.x, Math.max(v2.x, v3.x))));
        int minY = (int) Math.max(0, Math.ceil(Math.min(v1.y, Math.min(v2.y, v3.y))));
        int maxY = (int) Math.min(img.getHeight() - 1, Math.floor(Math.max(v1.y, Math.max(v2.y, v3.y))));

        double triangleArea = (v1.y - v3.y) * (v2.x - v3.x) + (v2.y - v3.y) * (v3.x - v1.x);

        for (int y = minY; y <= maxY; y++) {
            for (int x = minX; x <= maxX; x++) {
                double b1 = ((y - v3.y) * (v2.x - v3.x) + (v2.y - v3.y) * (v3.x - x)) / triangleArea;
                double b2 = ((y - v1.y) * (v3.x - v1.x) + (v3.y - v1.y) * (v1.x - x)) / triangleArea;
                double b3 = ((y - v2.y) * (v1.x - v2.x) + (v1.y - v2.y) * (v2.x - x)) / triangleArea;

                if (b1 >= 0 && b1 <= 1 && b2 >= 0 && b2 <= 1 && b3 >= 0 && b3 <= 1) {
                    double depth = b1 * v1.z + b2 * v2.z + b3 * v3.z;
                    double padding_distance = 0.03;
                    int zIndex = y * img.getWidth() + x;
                    
                    boolean isEdgePixel = (Math.abs(b1) < padding_distance || Math.abs(b2) < padding_distance || Math.abs(b3) < padding_distance);

                    if (b1 == 0 || b2 == 0 || b3 == 0) {
                        isEdgePixel = true;
                    }

                    if (zBuffer[zIndex] < depth) {
                        if (isEdgePixel) {
                            img.setRGB(x, y, t.color.darker().darker().getRGB());
                        } else {
                            img.setRGB(x, y, t.color.getRGB());
                        }
                        zBuffer[zIndex] = depth;
                    }
                }
            }
        }
    }


    public void load() {
        Json2DArrayHandler j2ah = new Json2DArrayHandler();

        ArrayList<int[]> faces = j2ah.loadArrayList("faces");

        double[][] vertices2D = j2ah.loadArray2("vertices2D");

        colors_old  = j2ah.loadArray(tf.getText()); //def moved
        //System.out.println(Arrays.deepToString(colors_old)); //debug

        Vertex[] vertices = new Vertex[vertices2D.length];
        for (int i = 0; i < vertices2D.length; i++) {
            vertices[i] = new Vertex(vertices2D[i][0], vertices2D[i][1], vertices2D[i][2]);
        }

        for (int i = 0; i < faces.size(); i++) {
            int[] face = faces.get(i); 
            Vertex[] temp = new Vertex[face.length];
            for (int j = 0; j < face.length; j++) {
                temp[j] = vertices[face[j]];
            }
            shapes.add(new Shape(temp, new Color(70, 70, 70)));
        }
    }
}

class Matrix3 {
    double[] values;
    Matrix3(double[] values) {
        this.values = values;
    }
    Matrix3 multiply(Matrix3 other) {
        double[] result = new double[9];
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                for (int i = 0; i < 3; i++) {
                    result[row * 3 + col] +=
                        this.values[row * 3 + i] * other.values[i * 3 + col];
                }
            }
        }
        return new Matrix3(result);
    }
    Vertex transform(Vertex in) {
        return new Vertex(
            in.x * values[0] + in.y * values[3] + in.z * values[6],
            in.x * values[1] + in.y * values[4] + in.z * values[7],
            in.x * values[2] + in.y * values[5] + in.z * values[8]
        );
    }
}

class Json2DArrayHandler {
    public static void main(String[] args) {
    }

    public static double[][] loadArray(String name) {
        String filePath = name + ".json";
        try {
            String loadedJson = Files.readString(Paths.get(filePath));
            return jsonToArrayDouble(loadedJson);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return new double[0][0]; 
    }


    public static ArrayList<int[]> loadArrayList(String name) {
        String filePath = name + ".json";
        try {
            String loadedJson = Files.readString(Paths.get(filePath));
            return jsonToArrayList(loadedJson);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return new ArrayList<>();
    }


    public static void saveArray(int[][] array, String name) {
        String filePath = name + ".json";
        String json = arrayToJson(array);
        try {
            Files.write(Paths.get(filePath), json.getBytes());
            System.out.println("JSON Saved: \n" + json);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static double[][] loadArray2(String name) {
        String filePath = name + ".json";
        try {
            String loadedJson = Files.readString(Paths.get(filePath));
            double[][] loadedArray = jsonToArrayDouble(loadedJson); 
            return loadedArray;
        } catch (IOException e) {
            e.printStackTrace();
        }
        return new double[0][0];
    }

    public static void saveArray2(double[][] array, String name) {
        String filePath = name + ".json";
        String json = arrayToJson(array);
        try {
            Files.write(Paths.get(filePath), json.getBytes());
            System.out.println("JSON Saved: \n" + json);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public static ArrayList<int[]> jsonToArrayList(String json) {
        json = json.trim();
        json = json.substring(1, json.length() - 1); // we here get rid of te []s
        String[] rows = json.split("\\],\\[");

        // array list
        ArrayList<int[]> arrayList = new ArrayList<>();

        
        for (String row : rows) {
            String[] columns = row.replace("[", "").replace("]", "").split(",");
            int[] rowArray = new int[columns.length];
            for (int j = 0; j < columns.length; j++) {
                rowArray[j] = Integer.parseInt(columns[j].trim());
            }
            arrayList.add(rowArray);
        }
        return arrayList;
    }
    
    public static int[][] jsonToArrayInt(String json) {
        json = json.trim();
        json = json.substring(1, json.length() - 1); // Remove outer brackets: [ ... ]
        String[] rows = json.split("\\],\\[");

        // Count the number of rows and columns
        int rowCount = rows.length;
        int columnCount = rows[0].split(",").length;

        // Initialize the 2D array
        int[][] array = new int[rowCount][columnCount];

        // Populate the 2D array with values from the JSON string
        for (int i = 0; i < rowCount; i++) {
            String[] columns = rows[i].replace("[", "").replace("]", "").split(",");
            for (int j = 0; j < columnCount; j++) {
                array[i][j] = Integer.parseInt(columns[j].trim());
            }
        }
        return array;
    }

    // startubg
    public static double[][] jsonToArrayDouble(String json) {
        json = json.trim();

        // Remove outer brackets — make sure they are there
        if (json.startsWith("[") && json.endsWith("]")) {
            json = json.substring(1, json.length() - 1);
        } else {
            throw new IllegalArgumentException("Invalid JSON array format");
        }

        // Split rows by "],[" but allow optional spaces and newlines between them
        String[] rows = json.split("\\],\\s*\\[");

        int rowCount = rows.length;
        int columnCount = -1;

        // Initialize the array with the first row's column count
        for (int i = 0; i < rowCount; i++) {
            // Remove any remaining brackets from the row strings
            rows[i] = rows[i].replace("[", "").replace("]", "").trim();

            String[] cols = rows[i].split(",");

            if (columnCount == -1) {
                columnCount = cols.length;
            } else if (cols.length != columnCount) {
                throw new IllegalArgumentException("Inconsistent column count at row " + i);
            }
        }

        double[][] array = new double[rowCount][columnCount];

        // Parse all elements to double
        for (int i = 0; i < rowCount; i++) {
            String[] cols = rows[i].split(",");
            for (int j = 0; j < columnCount; j++) {
                array[i][j] = Double.parseDouble(cols[j].trim());
            }
        }

        return array;
    }

    // to json
    public static String arrayToJson(int[][] array) {
        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < array.length; i++) {
            json.append(Arrays.toString(array[i]));
            if (i < array.length - 1) json.append(",");
        }
        json.append("]");
        return json.toString();
    }

    // for double
    public static String arrayToJson(double[][] array) {
        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < array.length; i++) {
            json.append(Arrays.toString(array[i]));
            if (i < array.length - 1) json.append(",");
        }
        json.append("]");
        return json.toString();
    }
}

class Vertex {
    double x,y,z;
    Vertex(double x, double y, double z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

class Shape {
    Vertex[] sides;
    Color color;
    Shape(Vertex[] sides, Color color) {
        this.sides = sides;
        this.color = color;
    }
}

class Triangle {
    Vertex v1, v2, v3;
    Color color;
    Triangle(Vertex v1, Vertex v2, Vertex v3, Color color) {
        this.v1 = v1;
        this.v2 = v2;
        this.v3 = v3;

        this.color = color;
    }
}

