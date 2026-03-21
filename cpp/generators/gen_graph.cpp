#include<iostream>
#include<random>
#include<set>
#include<vector>
#include<cstdlib>
#include<algorithm> 
int main(int argc,char* argv[]){
    // 参数：节点数 n，边数 m
    int n=(argc>1)?std::atoi(argv[1]):10;
    int m=(argc>2)?std::atoi(argv[2]):n*(n-1)/2; // 默认完全图
    if(m>n*(n-1)/2) m=n*(n-1)/2;             // 限制最大边数
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> vertex(1,n);
    std::set<std::pair<int,int>> edges;
    while(edges.size()<(size_t)m){
        int u=vertex(gen);
        int v=vertex(gen);
        if(u==v) continue;   // 不要自环
        if(u>v) std::swap(u,v); // 统一顺序，便于去重
        edges.insert({u,v});
    }
    std::cout<<n<<'\n'<<m<<'\n';
    for(const auto &S:edges)
        std::cout<<S.first<< ' '<<S.second<< '\n';
}

// 简单的随机图（之后可能利用洗牌优化）