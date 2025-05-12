import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  'bolt://localhost:7687', // Neo4j 数据库地址
  neo4j.auth.basic('neo4j', '12345678') // 用户名和密码
);

export const query = async (cypher, params = {}) => {
  const session = driver.session();
  try {
    const result = await session.run(cypher, params);
    return result.records;
  } catch (error) {
    console.error('Neo4j query error:', error);
  } finally {
    session.close();
  }
};
