using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TSP
{
    class Program
    {
        static void Main(string[] args)
        {
            коммивояжера problem = new коммивояжера();
            problem.FilePath = "city.txt";
            problem.Anneal();

            string path = "";
            for (int i = 0; i < problem.CitiesOrder.Count - 1; i++)
            {
                path += problem.CitiesOrder[i] + " -> ";
            }
            path += problem.CitiesOrder[problem.CitiesOrder.Count - 1];

            Console.WriteLine("KAROTIKA PUTI: " + path);

            Console.WriteLine("SAMAYA KAROTIKA RASTAYANI: " + problem.ShortestDistance.ToString());

            Console.ReadLine();
        }
    }
}
