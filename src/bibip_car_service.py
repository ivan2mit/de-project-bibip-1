from datetime import datetime
from decimal import Decimal
from typing import List
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
DB_PATH = 'src/db/'
BLOCK_SIZE = 501


class CarService:
    def row_create(*args) -> str:
        finall_row:str = str(args[0])
        for param in args[1:]:
            finall_row += '\t'+ str(param)
        return finall_row
    
    # crud
    def create(self, relation: str, pk: str, row: str):
        db_path = self.root_directory_path+ '/' + relation + '.txt'
        db_index_path = self.root_directory_path + '/' + 'index_' + relation + '.txt'
        num_row = 1
        try:
            with open(db_index_path, 'r+') as f:
                title = f.readline()
                data = f.readlines()
                end_row = data[-1].rstrip().split() if data else []
                if len(end_row) == 0:
                    data_nr = 0
                else:
                    data_nr = int(end_row[1])

                if len(data) > 0:
                    for line in data:
                        i_pk, i_num_row = line.split()
                        if i_pk == str(pk):
                            raise ValueError('Запись с таким ключом уже существует')
                new_row = str(pk)+'\t'+str(data_nr+1)
                f.write(new_row.ljust(BLOCK_SIZE-1)+'\n')
        except ValueError as ve:
            print(ve)
            return
        with open(db_path, 'a+') as f:
            f.write(row+(BLOCK_SIZE-len(row)-1)*' '+'\n')

    
    def read(self, relation: str, pk: str) -> List[str]:
        db_path = self.root_directory_path + '/' + relation + '.txt'
        db_index_path = self.root_directory_path + '/' + 'index_' + relation + '.txt'
        num_row = 0 
        relation_title = ''
        with open(db_index_path, 'r') as f:
            title = f.readline()
            while True:
                line = f.readline().rstrip().split()
                if len(line) != 0:
                    if line[0] == str(pk):
                        num_row = int(line[1])
                        break
                else:
                    return []
            
        with open(db_path, 'r') as f:
            relation_title = f.readline().rstrip().split()
            f.seek(num_row * BLOCK_SIZE)
            return [relation_title, f.readline().rstrip().split()]
    

    def update(self, relation:str, pk: str, row:str) -> List[str]:
        db_path = self.root_directory_path + '/' + relation + '.txt'
        db_index_path = self.root_directory_path + '/' + 'index_' + relation + '.txt'
        relation_title = ''
        with open(db_index_path, 'r') as f:
            title = f.readline()
            while True:
                line = f.readline().rstrip().split()
                if len(line) != 0:
                    if line[0] == str(pk):
                        num_row = int(line[1])
                        break
                else:
                    return []
        with open(db_path, "r+") as f:
            f.seek(num_row * BLOCK_SIZE)
            f.write(row.ljust(BLOCK_SIZE-1)+'\n')
            return [relation_title, f.readline().rstrip().split()]
        

    def delele(self, relation: str, num_row:int):
        pass

    
    def find_equal(self, relation: str, column_name: str, value: str) -> List[List]:
        db_path = self.root_directory_path + '/' + relation + '.txt'
        result = []
        with open(db_path, 'r') as f:
            title = f.readline().rstrip().split()
            result.append(title)
            num_col = title.index(column_name)

            while True:
                row = f.readline().rstrip().split()
                if row != []:
                    if row[num_col] == value:
                        result.append(row)
                else:
                    break
        return result

    def create_relation(self, relation_name: str, title: str):
        db_path = self.root_directory_path + '/' + relation_name + '.txt'
        with open(db_path, 'w') as f:
            f.write(title.ljust(BLOCK_SIZE-1)+'\n')
        db_index_path = self.root_directory_path + '/' + 'index_' + relation_name + '.txt'
        with open(db_index_path, 'w') as f:
            index_title = title.split()[0] + '\t' + 'num_row'
            f.write(index_title.ljust(BLOCK_SIZE-1)+'\n')

    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.create_relation('models', 'id\tname\tbrand')
        self.create_relation('cars', 'vin\tmodel\tprice\tdate_start\tstatus')
        self.create_relation('sales', 'sales_number\tcar_vin\tsales_date\tcost')

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        id = model.id
        name = model.name
        brand = model.brand
        CarService.create(self, 'models', id, str(id)+'\t'+name+'\t'+brand)
        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        
        vin = car.vin
        model = car.model
        price = str(car.price)
        date_start = str(car.date_start.date())
        status = str(car.status)

        find_model = CarService.read(self, 'models', model)
        if find_model != []:
            new_row = CarService.row_create(vin, model, price, date_start, status)
            CarService.create(self, 'cars', vin, new_row)
            return car
        else:
            print('модель автомобиля не найдена')
            return None

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sale_number = sale.sales_number
        car_vin = sale.car_vin
        sales_date = str(sale.sales_date.date())
        cost = str(sale.cost)
        car = Car(
            vin="",
            model=0,
            price=Decimal("0"),
            date_start=datetime.now().date(),
            status=CarStatus.available,
        )

        find_car = CarService.read(self, 'cars', car_vin)
        if len(find_car) > 1:
            car.vin = find_car[1][0]
            car.model = int(find_car[1][1]) 
            car.price = Decimal(find_car[1][2])
            date = find_car[1][3].split('-')
            car.date_start = datetime(int(date[0]),int(date[1]),int(date[2])).date()
            car.status = find_car[1][4]
            new_row = CarService.row_create(sale_number, car_vin, sales_date, cost)
            CarService.create(self, 'sales', sale_number, new_row)
            new_status = CarService.row_create(
                                                car.vin,
                                                car.model,
                                                car.price,
                                                car.date_start,
                                                CarStatus.sold)
            CarService.update(self, 'cars', car.vin, new_status)
        else : 
            print('Автомобиль не найден')

        return car
            
    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars_list = []
        raw_cars = CarService.find_equal(self, 'cars', 'status', str(status))[1:]
        for row in raw_cars:
            car = Car(
                vin=row[0],
                model=int(row[1]),
                price=Decimal(row[2]),
                date_start=datetime.strptime(row[3], '%Y-%m-%d').date(),
                status=CarStatus(row[4])
            )
            cars_list.append(car)
        return cars_list

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:

        car = CarFullInfo(
            vin="",
            price=Decimal("0"),
            date_start=datetime.now().date(),
            status=CarStatus.available,
            car_model_name="",
            car_model_brand="",
            sales_date=None,
            sales_cost=None,
        )
        find_car = CarService.read(self, 'cars', vin)
        if len(find_car) > 1:
            car.vin = find_car[1][0]
            model = int(find_car[1][1])
            car.price = Decimal(find_car[1][2])
            car.date_start = datetime.strptime(find_car[1][3], '%Y-%m-%d')
            car.status = CarStatus(find_car[1][4])
            find_model = CarService.read(self, 'models', model)
            if len(find_model) > 1:
                car.car_model_name = find_model[1][1]
                car.car_model_brand = find_model[1][2]
            find_sale = CarService.find_equal(self, 'sales', 'car_vin', car.vin)
            if len(find_sale) > 1:
                date = find_sale[1][2].split('-')
                car.sales_date = datetime(int(date[0]),int(date[1]),int(date[2]))
                car.sales_cost = Decimal(find_sale[1][3])
        else : 
            print('Автомобиль не найден')
            return None
        return car

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        pk = vin
        db_path = self.root_directory_path + '/' + 'cars' + '.txt'
        db_index_path = self.root_directory_path + '/' + 'index_' + 'cars' + '.txt'
        with open(db_index_path, 'r+') as f:
            title = f.readline()
            num_index_row = 0
            old_row = []
            while True:
                line = f.readline().rstrip().split()
                num_index_row += 1
                if len(line) != 0:
                    if line[0] == str(pk):
                        num_row = int(line[1])
                        old_row = line
                        break
                else:
                    return None
            
            f.seek(num_index_row * BLOCK_SIZE)
            new_row = CarService.row_create(new_vin, old_row[1])
            f.write(new_row.ljust(BLOCK_SIZE-1)+'\n')
            
        with open(db_path, 'r+') as f:
            f.seek(num_row * BLOCK_SIZE)
            old_row = f.readline().rstrip().split()
            old_row[0] = new_vin
            new_row = CarService.row_create(*old_row)
            f.seek(num_row * BLOCK_SIZE)
            f.write(new_row.ljust(BLOCK_SIZE-1)+'\n')

        car = Car(
            vin=new_vin,
            model=int(old_row[1]),
            price=Decimal(old_row[2]),
            date_start=datetime.strptime(old_row[3], '%Y-%m-%d').date(),
            status=CarStatus(old_row[4])
        )
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        pk = sales_number
        sale = CarService.read(self, 'sales', sales_number)
        car_vin =  sale[1][1]
        car = CarService.read(self, 'cars', car_vin)
        car[1][4] = str(CarStatus.available)
        new_row = CarService.row_create(*car[1])
        car = CarService.update(self, 'cars', car_vin, new_row)
        CarService.update(self, 'sales', sales_number, CarService.row_create('delete_data','delete_data','delete_data','delete_data'))
        db_index_path = self.root_directory_path + '/' + 'index_' + 'sales' + '.txt'
        with open(db_index_path, 'r+') as f:
            title = f.readline()
            num_index_row = 0
            while True:
                line = f.readline().rstrip().split()
                num_index_row += 1
                if len(line) != 0:
                    if line[0] == str(pk):
                        break
                else:
                    return None
            f.seek(num_index_row * BLOCK_SIZE)
            f.write('delete_data\tdelete_data'.ljust(BLOCK_SIZE-1)+'\n')
        reverted_car = Car(
            vin=car[1][0],
            model=int(car[1][1]),
            price=Decimal(car[1][2]),
            date_start=datetime.strptime(car[1][3], '%Y-%m-%d').date(),
            status=CarStatus(car[1][4])
        )
        return reverted_car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        car_sale_list = CarService.find_equal(self, 'cars', 'status', 'sold')
        rating = {}
        for car in car_sale_list[1:]:
            if car[1] in rating:
                rating[car[1]].append(car[2])
            else:
                rating[car[1]] = [car[2]]
        rating_data = []
        for model, sales in rating.items():
            rating_data.append([model, len(sales), max(sales)])

        sorted_rating = sorted(rating_data,key = lambda data: (data[1], data[2]), reverse=True)[:3]
        responce = []
        for model in sorted_rating:
            model_data = CarService.read(self, 'models', model[0])
            responce.append(ModelSaleStats(car_model_name=model_data[1][1], brand=model_data[1][2], sales_number=model[1]))
        return responce


        