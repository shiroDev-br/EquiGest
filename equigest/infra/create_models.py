import asyncio

from equigest.infra.database import mapper_registry, engine

async def create_models():
    async with engine.begin() as conn:
        from equigest.models.mares import Mare
        from equigest.models.user import User
        await conn.run_sync(mapper_registry.metadata.create_all)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_models())