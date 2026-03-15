
#include <stdio.h>
#include <string.h>

typedef struct {
    int id;
    char name[100];
} users;

users users_data[] = {
    { 1, "Alice" },
    { 2, "Alice" },
    { 3, "Alice" }
};

int users_count = sizeof(users_data) / sizeof(users_data[0]);

int main() {

for(int i = 0; i < users_count; i++) {

if (((users_data[i].id > 0) && (strcmp(users_data[i].name, "Alice") == 0))) {

printf("%d ", users_data[i].id);

printf("%s ", users_data[i].name);

printf("\n");

}

}

return 0;
}
