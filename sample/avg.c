float avg(int length, int *value) {
	int i;
	float total;
	total = 0;
	for(i = 0; i < length; i++) {
		total = total + value[i];
	}

	return (total / length);
}

int main(void) {
	int count, i, total;
	int record[5];
	float average;

	count = 5;
	total = 0;

	for(i = 0; i < count; i++) {
		record[i] = i * 1;
		printf("value : ");
		printf("%d\n", record[i]);
	}

	printf("\nStart...\n");

	for(i = 0; i < count; i++) {
		average = avg(i + 1, record);
		total = total + average;
		printf("Average : ");
		printf("%f\n", average);
		if(total > 3) {
			printf("*** total exceeds 3!***\n");
		}
	}

	printf("Done!\n");

}
