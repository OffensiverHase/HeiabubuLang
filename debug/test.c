int* lst() {
    int ret[] = {1,2,3};
    return ret;
}

int main() {
    int* arr = lst();
    arr[1];
    return 0;
}