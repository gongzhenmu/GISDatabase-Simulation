class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_name, columns):
        if table_name in self.tables:
            print(f"Table '{table_name}' already exists.")
            return
        self.tables[table_name] = {"columns": columns, "data": []}

    def insert_data(self, table_name, data):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        columns = self.tables[table_name]["columns"]
        if len(data) != len(columns):
            data = data[0:len(columns)]

        self.tables[table_name]["data"].append(dict(zip(columns, data)))

    def select_data(self, table_name, columns=None, condition=None):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return

        if columns is None:
            columns = self.tables[table_name]["columns"]

        selected_data = []
        for row in self.tables[table_name]["data"]:
            if condition is None or condition(row):
                selected_data.append({column: row[column] for column in columns})

        return selected_data

    def delete_data(self, table_name, condition=None):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return

        self.tables[table_name]["data"] = [
            row for row in self.tables[table_name]["data"] if condition is None or not condition(row)
        ]

    def print_table(self, table_name, selected_data=None):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return

        if selected_data is None:
            data = self.select_data(table_name)
            column_names = self.tables[table_name]["columns"]
        else:
            data = selected_data
            column_names = list(data[0].keys()) if data else []

        column_widths = [len(str(column)) for column in column_names]
        for row in data:
            for idx, column in enumerate(column_names):
                column_widths[idx] = max(column_widths[idx], len(str(row[column])))

        def print_horizontal_line():
            line = "+" + "+".join("-" * (width + 2) for width in column_widths) + "+"
            print(line)

        def print_row(row_data):
            row = "|" + "|".join(f" {str(value).ljust(width)} " for width, value in zip(column_widths, row_data)) + "|"
            print(row)

        print_horizontal_line()
        print_row(column_names)
        print_horizontal_line()
        for row in data:
            print_row([row[column] for column in column_names])
        print_horizontal_line()
        print("Total rows:",len(data))
        
    def delete_table(self, table_name):
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return
        del self.tables[table_name]
        print(f"Table '{table_name}' deleted.")

