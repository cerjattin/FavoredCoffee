from fastapi import HTTPException
import pandas as pd
from sqlmodel import Session, select
from ..models import Product
from io import BytesIO

def process_inventory_file(db: Session, file_content: bytes, file_type: str):
    """
    Procesa un archivo de inventario.
    Reglas: Transacción Atómica (A), Actualización de Precios (1), Stock Negativo (2).
    """
    try:
        buffer = BytesIO(file_content)
        if file_type == "text/csv":
            df = pd.read_csv(buffer)
        elif file_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]:
            buffer.seek(0)
            df = pd.read_excel(buffer)
        else:
            raise ValueError("Formato de archivo no soportado (usar CSV o Excel)")

        df.columns = [col.lower().strip() for col in df.columns]

        required_cols = {"sku", "name", "category", "price", "stock_a_sumar"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Columnas faltantes. Se requieren: {required_cols}")

    except Exception as e:
        # Error leyendo el archivo
        raise HTTPException(status_code=400, detail=f"Error leyendo el archivo: {str(e)}")

    # Inicio de la lógica transaccional
    try:
        creados = 0
        actualizados = 0

        # Validar todo el archivo antes de aplicar cambios
        for index, row in df.iterrows():
            if pd.isna(row["sku"]) or pd.isna(row["name"]) or pd.isna(row["category"]):
                raise ValueError(f"Fila {index+2}: 'sku', 'name' y 'category' no pueden estar vacíos")
            if not isinstance(row["price"], (int, float)) or row["price"] <= 0:
                raise ValueError(f"Fila {index+2}: 'price' debe ser un número positivo")
            if not isinstance(row["stock_a_sumar"], (int, float)):  # float por si pandas lo lee así
                raise ValueError(f"Fila {index+2}: 'stock_a_sumar' debe ser un número")

        # Si todas las validaciones pasan, aplicamos los cambios
        for _, row in df.iterrows():
            product_sku = str(row["sku"])

            product = db.exec(
                select(Product).where(Product.sku == product_sku)
            ).first()

            stock_a_sumar = int(row["stock_a_sumar"])

            if product:
                # Actualizar (Regla 1)
                product.name = row["name"]
                product.category = row["category"]
                product.price = float(row["price"])
                product.stock += stock_a_sumar  # (Regla 2: permite negativos)
                actualizados += 1
            else:
                # Crear nuevo
                product = Product(
                    sku=product_sku,
                    name=row["name"],
                    category=row["category"],
                    price=float(row["price"]),
                    stock=stock_a_sumar,
                )
                creados += 1

            db.add(product)

        # Si todo fue bien, guardar cambios
        db.commit()

        return {
            "status": "success",
            "summary": f"{actualizados} productos actualizados, {creados} creados",
        }

    except Exception as e:
        # Regla 3 (Atomicidad): Si algo falla, revertir todo
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Transacción fallida (revertida): {str(e)}")
