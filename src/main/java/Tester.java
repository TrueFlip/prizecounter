/**
 * Created by felixsidokhine on 2018-03-11.
 */

import org.apache.commons.math3.random.MersenneTwister;
import java.util.ArrayList;
import java.util.Scanner;


public class Tester {

    public static void main(String args[]){
        Scanner scanner = new Scanner(System.in);
        System.out.println("Please input the seed used by the MT...");
        long seed = Long.parseLong(scanner.next());
        System.out.println("Please input the iterations at which your numbers were obtained...");
        ArrayList<Long> numbers = new ArrayList<Long>();
        ArrayList<Long> results = new ArrayList<Long>();
        String[] strings = scanner.next().split(",");
        for(String s: strings){
            numbers.add(Long.parseLong(s));
        }
        //Informational purposes...
        System.out.println("Your seed is: " + seed);
        System.out.println("Your iterations are: " + numbers);
        MersenneTwister twister = new MersenneTwister();
        for(Long iteration: numbers){
            twister.setSeed(seed);
            long x = -1L;
            for(int i=0;i<iteration+1;i++){
                x = twister.nextLong(8);
            }
            results.add(x);
        }
        System.out.println("Your combination was: " + results);
    }
}
