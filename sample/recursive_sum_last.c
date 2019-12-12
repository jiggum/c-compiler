int sum(int num) {
 if (num > 0) {
 num = num + sum(num - 1);
 }
 return num;
}

int main(void) {
 int a;
a = sum(50);
printf("%d\n", a);
}
