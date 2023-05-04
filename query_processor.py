import re
class QueryProcessor:
    def __init__(self, database):
        self.database = database

    def process_query(self, query):
        query = query.strip().lower()
        if query.startswith("create table"):
            self.create_table(query)
        elif query.startswith("insert"):
            self.insert_data(query)
        elif query.startswith("select"):
            self.select_data(query)
        elif query.startswith("delete"):
            self.delete_data(query)
        elif query.startswith("drop table"):
            self.delete_table(query)
        else:
            print("Invalid query")

    def create_table(self, query):
        match = re.match(r"create table (\w+) \((.+)\)", query)
        if match:
            table_name = match.group(1)
            columns = [column.strip() for column in match.group(2).split(",")]
            self.database.create_table(table_name, columns)
            print(f"Table '{table_name}' created.")
        else:
            print("Invalid CREATE TABLE query")

    def insert_data(self, query):
        match = re.match(r"insert into (\w+) values \((.+)\)", query)
        if match:
            table_name = match.group(1)
            data = [value.strip() for value in match.group(2).split(",")]
            try:
                int_data = []
                for item in data:
                    if re.match(r"-?\d+(\.\d+)?$", item):
                        if '.' in item:
                            int_data.append(float(item))
                        else:
                            int_data.append(int(item))
                    else:
                        int_data.append(item)
            except ValueError:
                print("Invalid data value in INSERT query")
                return

            self.database.insert_data(table_name, int_data)
            # print(f"Data inserted into table '{table_name}'.")
        else:
            print("Invalid INSERT query")

    def select_data(self, query, output=True):
        match = re.match(r"select (.+) from (\w+)(?: where (.*))?", query)
        if match:
            columns = [column.strip() for column in match.group(1).split(",")] if match.group(1) != "*" else None
            table_name = match.group(2)
            condition_str = match.group(3)

            if condition_str:
                condition_parts = re.findall(r"(\w+)\s*([\>\<\=\!]+)\s*(-?\d+(\.\d+)?)", condition_str)
                if condition_parts:
                    conditions = []
                    for condition_part in condition_parts:
                        column, operator, value = condition_part[0], condition_part[1], condition_part[2]
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                        if operator == "=":
                        	operator = "=="
                        conditions.append(lambda row, col=column, op=operator, val=value: eval(f"row[col] {op} val"))

                    condition = lambda row: all([cond(row) for cond in conditions])
                else:
                    print("Invalid condition in SELECT query")
                    return
            else:
                condition = None

            selected_data = self.database.select_data(table_name, columns, condition)
            if output:
                self.database.print_table(table_name, selected_data=selected_data)
            return selected_data
        else:
            print("Invalid SELECT query")


    def delete_data(self, query):
        match = re.match(r"delete from (\w+)(?: where (.*))?", query)
        if match:
            table_name = match.group(1)
            condition_str = match.group(2)

            if condition_str:
                condition_parts = re.match(r"(\w+)\s*([\>\<\=\!]+)\s*(\w+)", condition_str)
                if condition_parts:
                    column, operator, value = condition_parts.group(1), condition_parts.group(2), condition_parts.group(3)
                    try:
                        value = int(value) if value.isdigit() else value
                        condition = lambda row: eval(f"row['{column}'] {operator} {value}")
                    except Exception as e:
                        print("Query type not supported. (Try == instead of =)")

                else:
                    print("Invalid condition in DELETE query")
                    return
            else:
                condition = None

            self.database.delete_data(table_name, condition)
            print(f"Data deleted from table '{table_name}'.")
        else:
            print("Invalid DELETE query")

    def delete_table(self, query):
        match = re.match(r"drop table (\w+)", query)
        if match:
            table_name = match.group(1)
            self.database.delete_table(table_name)
        else:
            print("Invalid DROP TABLE query")
