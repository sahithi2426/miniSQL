C_HEADER = """
#include <stdio.h>
#include <string.h>
"""

MAIN_START = """
int main() {
"""

MAIN_END = """
return 0;
}
"""

TABLE_STRUCT_TEMPLATE = """
typedef struct {{
{fields}
}} {table_name};
"""

TABLE_DATA_TEMPLATE = """
{table_name} {table_name}_data[] = {{
{rows}
}};
"""

ROW_TEMPLATE = "    {{ {values} }}"

ROW_COUNT_TEMPLATE = """
int {table_name}_count = sizeof({table_name}_data) / sizeof({table_name}_data[0]);
"""

SCAN_LOOP_START = """
for(int i = 0; i < {table_name}_count; i++) {{
"""

SCAN_LOOP_END = """
}
"""

FILTER_TEMPLATE = """
if ({condition}) {{
"""

FILTER_END = """
}
"""

PRINT_TEXT_TEMPLATE = """
printf("%s ", {table_name}_data[i].{column});
"""

PRINT_INT_TEMPLATE = """
printf("%d ", {table_name}_data[i].{column});
"""

PRINT_NEWLINE = """
printf("\\n");
"""