#include<iostream>
#include<random>
#include<cstdlib>
int main(int argc,char* argv[]){
    int n=(argc>1)?std::atoi(argv[1]):10;
    int min_val=(argc>2)?std::atoi(argv[2]):1;
    int max_val=(argc>3)?std::atoi(argv[3]):100;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(min_val,max_val);
    std::cout<<n<<'\n';
    for(int i=1;i<=n;++i) 
        std::cout<<dist(gen)<<(i==n?'\n':' ');
}
// 参数：个数，最大值，最小值