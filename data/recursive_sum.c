int sum(int num)
{
  int result;
  if(num > 1)
  {
    result = num + sum(num-1);
  }
  else
  {
    result = num;
  }

  printf("%d added\n", num);
  return result;
}


int main(void)
{
  int result;
  result = sum(8);
  printf("\nTotal : %d\n", result);
}