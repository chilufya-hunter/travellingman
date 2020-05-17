//(Коммивояжёр (фр. commis voyageur) — бродячий торговец.
//Задача коммивояжёра — важная задача транспортной логистики, отрасли,
//занимающейся планированием транспортных перевозок.Коммивояжёру, 
//следует объехать n пунктов и в конце концов вернуться в исходный пункт.
 ///Требуется определить наиболее выгодный маршрут объезда.
//В качестве меры выгодности маршрута (точнее говоря, невыгодности)
 ///может служить суммарное время в пути, суммарная стоимость дороги,
 //или, в простейшем случае, длина маршрута._




using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace TSP
{
    public class коммивояжера
    {
        private string filePath;
        private List<int> currentOrder = new List<int>();
        private List<int> nextOrder = new List<int>();
        private double[,] distances;
        private Random random = new Random();
        private double shortestDistance = 0;

        public double ShortestDistance
        {
            get
            {
                return shortestDistance;
            }
            set
            {
                shortestDistance = value;
            }
        }

        public string FilePath
        {
            get
            {
                return filePath;
            }
            set
            {
                filePath = value;
            }
        }

        public List<int> CitiesOrder
        {
            get
            {
                return currentOrder;
            }
            set
            {
                currentOrder = value;
            }
        }

        
        /// Загрузка городов из текстового файла, представляющего матрицу смежности
        
        private void LoadCities()
        {
            StreamReader reader = new StreamReader(filePath);

            string cities = reader.ReadToEnd();

            reader.Close();

            string[] rows = cities.Split('\n');

            distances = new double[rows.Length, rows.Length];

            for (int i = 0; i < rows.Length; i++)
            {
                string[] distance = rows[i].Split(' ');
                for (int j = 0; j < distance.Length; j++)
                {
                    distances[i, j] = double.Parse(distance[j]);
                }

                //количество строк в этой матрице представляет собой количество городов
                //мы представляем каждый город по индексу от 0 до N-1
                //где N-общее количество городов
                currentOrder.Add(i);
            }

            if (currentOrder.Count < 1)
                throw new Exception("No cities to order.");
        }

        
        /// Вычислите общее расстояние, которое является целевой функцией
       
      
        private double GetTotalDistance(List<int> order)
        {
            double distance = 0;

            for (int i = 0; i < order.Count - 1; i++)
            {
                distance += distances[order[i], order[i + 1]];
            }

            if (order.Count > 0)
            {
                distance += distances[order[order.Count - 1], 0];
            }

            return distance;
        }


        ///Получите следующие случайные расположения городов

        /// <param name="order"></param>

        private List<int> GetNextArrangement(List<int> order)
        {
            List<int> newOrder = new List<int>();

            for (int i = 0; i < order.Count; i++)
                newOrder.Add(order[i]);

            //мы будем переставлять только два города случайным образом
            // начальная точка всегда должна быть нулевой - поэтому ноль не должен быть включен
            int firstRandomCityIndex = random.Next(1, newOrder.Count);
            int secondRandomCityIndex = random.Next(1, newOrder.Count);

            int dummy = newOrder[firstRandomCityIndex];
            newOrder[firstRandomCityIndex] = newOrder[secondRandomCityIndex];
            newOrder[secondRandomCityIndex] = dummy;

            return newOrder;
        }

       
        public void Anneal()
        {
            int iteration = -1;

            double temperature = 10000.0;
            double deltaDistance = 0;
            double coolingRate = 0.9999;
            double absoluteTemperature = 0.00001;

            LoadCities();

            double distance = GetTotalDistance(currentOrder);

            while (temperature > absoluteTemperature)
            {
                nextOrder = GetNextArrangement(currentOrder);

                deltaDistance = GetTotalDistance(nextOrder) - distance;

                //если новый ордер имеет меньшее расстояние
                //или если новый порядок имеет большее расстояние, но удовлетворяет условию Больцмана, то примите это расположение
                if ((deltaDistance < 0) || (distance > 0 && Math.Exp(-deltaDistance / temperature) > random.NextDouble()))
                {
                    for (int i = 0; i < nextOrder.Count; i++)
                        currentOrder[i] = nextOrder[i];

                    distance = deltaDistance + distance;
                }

                //охладите температуру
                temperature *= coolingRate;

                iteration++;
            }

            shortestDistance = distance;
        }
    }
}