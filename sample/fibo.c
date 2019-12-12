int fibo(int n)
{
  if (n <= 2)
  {
    return 1;
  }
  return fibo(n - 1) + fibo(n - 2);
}

int main(void)
{
  int n, result;
  n = 10;
  result = fibo(n);
  printf("%d\n", result);
}
