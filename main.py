import asyncio
import logging
from neigh.bet_tools.racing import Racing

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    # Create a racing scraper instance
    racing = Racing(channel="main")

    try:
        # Start polling (this will run continuously)
        await racing._start_polling()
    except KeyboardInterrupt:
        print("\nStopping scraper...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
