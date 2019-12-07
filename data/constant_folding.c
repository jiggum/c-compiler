int avg(int count, int *value)
{
  int i, total, a, c;
  total = count;
  total = 4;
  a = 3;
  for(i = 0; i < count; i++)
  {
    c = total;
    total = a;
    total = 4;
    total = total;
    total = 3;
  }

  return (total / count);
}

int main(void)
{
  int student_number, count, i, sum;
  int mark[4];
  float average;

  count = 4;
  sum = 4 + -count;

  for(i = 0; i < count; i++)
  {
    mark[i] = i * 30;
    sum = count;
    sum = sum + mark[i];
    average = avg(i + 1, mark);
    if(average > 23)
    {
      printf("%f\n", average);
    }
  }
}
