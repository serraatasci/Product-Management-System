#include<stdio.h>
#include<string.h>

#define FILE_PATH "Products.bin"

struct Products {
    int id;
    char product_name[100];
    char category[50];
    int stock;
    float price;
    char entry_date[15];
    char warehouse[50];
    char warehouse_id[10];
};

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif

EXPORT void add_product(int id, const char* product_name, const char* category, int stock, float price, const char* entry_date,const char* warehouse, const char* warehouse_id){
    FILE* file = fopen(FILE_PATH, "ab+");

    if (file == NULL){
        perror("\nError opening file!\n");
        return;
    }

    //Verileri struct içine kopyala
    struct Products p;
    p.id = id;
    strncpy(p.product_name, product_name, sizeof(p.product_name)-1);

    p.product_name[sizeof(p.product_name) - 1] = '\0';

    strncpy(p.category, category, sizeof(p.category) - 1);
    p.category[sizeof(p.category) - 1] = '\0';

    p.stock = stock;
    p.price = price;

    strncpy(p.entry_date, entry_date, sizeof(p.entry_date) - 1);
    p.entry_date[sizeof(p.entry_date) - 1] = '\0';

    strncpy(p.warehouse, warehouse, sizeof(p.warehouse) - 1);
    p.warehouse[sizeof(p.warehouse) - 1] = '\0';

    strncpy(p.warehouse_id, warehouse_id, sizeof(p.warehouse_id) - 1);
    p.warehouse_id[sizeof(p.warehouse_id) - 1] = '\0';

    // Veriyi dosyaya yaz
    fwrite(&p, sizeof(struct Products), 1, file);
    printf("\nThe product was successfully added.\n");

    fclose(file);
}


EXPORT void updated_product(int id_update, float price_update, int stock_update)
{
    FILE *file = fopen(FILE_PATH, "ab+");
    if (file == NULL)
    {
        perror("\nError opening file!\n");
        return;
    }

    FILE* temp_file = fopen("Temp_Products.bin", "wb");
    if (temp_file == NULL)
    {
        printf("\nError opening temporary file!\n");
        fclose(file);
        return;
    }
    struct Products p;
    int found = 0;

    while(fread(&p, sizeof(struct Products),1, file))
    {
        if (p.id == id_update) 
        {
            p.price = price_update;
            p.stock = stock_update;
            found = 1;
        }
        fwrite(&p, sizeof(struct Products), 1, temp_file);
    }
    fclose(file);
    fclose(temp_file);

    if (!found) {
        printf("\nProduct with ID %d not found.\n", id_update);
        remove("Temp_Products.bin");
        return;
    }

    if (remove(FILE_PATH) != 0) {
        perror("\nError removing file!\n");
        return;
    }

    if (rename("Temp_Products.bin", FILE_PATH) != 0) {
        perror("\nError renaming file!\n");
        return;
    }

    printf("\nProduct with ID %d has been updated.\n", id_update);

}

EXPORT int delete_product(int delete_id)
{
    FILE* file = fopen(FILE_PATH, "rb");
    if (file == NULL) {
        perror("\nError opening file!\n");
        return -1;
    }
    FILE* temp_file = fopen("Temp_Products.bin", "wb");
    if (temp_file == NULL) {
        perror("\nError opening temporary file!\n");
        fclose(file);
        return -1;
    }
    struct Products p;
    int found = 0;

    while (fread(&p, sizeof(struct Products), 1, file)) {
        if (p.id != delete_id) {
            fwrite(&p, sizeof(struct Products), 1, temp_file);
        } else {
            found = 1;
        }
    }

    fclose(file);
    fclose(temp_file);

    if (!found) {
        remove("Temp_Products.bin");  // Geçici dosyayı temizle
        return -1;  // Ürün bulunamadı
    }

    if (remove(FILE_PATH) != 0) {
        perror("\nError removing file!\n");
        return 0; 
    }

    if (rename("Temp_Products.bin", FILE_PATH) != 0) {
        perror("\nError renaming file!\n");
        return 0;  
    }

    return 1; 
}
   
EXPORT void list_product(){
    FILE* file = fopen(FILE_PATH, "rb");

    if (file == NULL) {
        perror("\nError opening file!\n");
        return;
    }
    struct Products p;
    while (fread(&p, sizeof(struct Products), 1, file)) {
        printf("\nProduct ID:%d\n", p.id);
        printf("Product Name : %s\n", p.product_name);
        printf("Category : %s\n", p.category);
        printf("Stock : %d\n", p.stock);
        printf("Price : %.2f\n", p.price);
        printf("Entry Date : %s\n", p.entry_date);
        printf("Warehouse : %s\n", p.warehouse);
        printf("Warehouse ID: %s\n", p.warehouse_id);
    }
    fclose(file);
}
