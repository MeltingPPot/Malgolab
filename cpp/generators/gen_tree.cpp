#include<iostream>
#include<vector>
#include<random>
#include<cstdlib>
#include<queue>
int main(int argc,char* argv[]){
    int n((argc>1)?std::atoi(argv[1]):10);
    if(n<2) n=2;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> vertex(1,n);
    std::vector<int> prufer(n-2),degree(n+1,1);
    for(int i=0;i<n-2;++i) prufer[i]=vertex(gen);
    for(int v:prufer) ++degree[v];
    std::priority_queue<int,std::vector<int>,std::greater<int>> leaves;
    for(int i=1;i<=n;++i) if(degree[i]==1) leaves.push(i);
    std::cout<<n<<'\n'<<n-1<<'\n';
    for(int v:prufer){
        int leaf=leaves.top();
        leaves.pop();
        std::cout<<leaf<<' '<<v<<'\n';
        --degree[leaf];
        --degree[v];
        if(degree[v]==1) leaves.push(v);
    }
    std::cout<<leaves.top()<<' ';
    leaves.pop();
    std::cout<<leaves.top()<<'\n';
    leaves.pop();
}
// 采用purfer序列生成